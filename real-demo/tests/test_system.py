import sys,json,unittest,tempfile,threading,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from governance import scan,qa,redact_code
from scheduling import validate_tasks,validate_schedule
from pipeline import initial,advance
from store import Store
from app import make_server
from llm import Gemini,ModelError

GOOD='import re\nimport os\nSECRET_KEY = os.getenv("SECRET_KEY")\ndef validate_email(email):\n    return re.fullmatch(r"[^@\\s]+@[^@.\\s]+(?:\\.[^@.\\s]+)+", email.strip()) is not None\n'
BAD=GOOD.replace('os.getenv("SECRET_KEY")','"FAKE_DO_NOT_KEEP"')
TASKS={'tasks':[{'id':'A','name':'A','steps':[{'machine':'Cắt','duration':3},{'machine':'Sơn','duration':2}]},{'id':'B','name':'B','steps':[{'machine':'Cắt','duration':2},{'machine':'Sơn','duration':4}]}],'unit':'phút','changes':[],'needs_clarification':False}
SCHEDULE={'schedule':[{'task_id':'B','step_id':1,'machine':'Cắt','start_time':0,'end_time':2},{'task_id':'A','step_id':1,'machine':'Cắt','start_time':2,'end_time':5},{'task_id':'B','step_id':2,'machine':'Sơn','start_time':2,'end_time':6},{'task_id':'A','step_id':2,'machine':'Sơn','start_time':6,'end_time':8}],'makespan':8}

class FakeModel:
    def __init__(self,bad_schedule=False):self.calls=[];self.bad_schedule=bad_schedule;self.dev_calls=0
    def call(self,role,instruction,payload):
        self.calls.append((role,payload))
        if role=='planner':data={'story':{'title':'Email','acceptance':['valid','invalid']}}
        elif role=='developer':
            if 'trusted_feedback' in payload:
                assert 'FAKE_DO_NOT_KEEP' not in payload['code_to_repair']
                data={'code':GOOD}
            else:data={'code':BAD}
        elif role=='seeker':data={'tasks':[{'id':'A','name':'A'},{'id':'B','name':'B'}]}
        elif role in ('weaver','verifier'):data=json.loads(json.dumps(TASKS))
        else:
            assert payload['verified']['tasks']==TASKS['tasks']
            data=json.loads(json.dumps(SCHEDULE))
            if self.bad_schedule and 'trusted_feedback' not in payload:data['schedule'][1]['start_time']=0
        return data,{'role':role,'provider':'TEST DOUBLE','model':'fake','seconds':0,'input_tokens':1,'output_tokens':1}

class GateTests(unittest.TestCase):
    def test_secret_and_environment(self):
        self.assertFalse(scan(BAD)['pass']);self.assertTrue(scan(GOOD)['pass'])
        self.assertNotIn('FAKE_DO_NOT_KEEP',redact_code(BAD))
    def test_concatenated_and_alias_secret(self):
        self.assertFalse(scan('PART="abc"\nAPI_KEY=PART+"xyz"\ndef validate_email(email):\n return True')['pass'])
    def test_environment_fallback_is_blocked(self):self.assertFalse(scan(GOOD.replace('os.getenv("SECRET_KEY")','os.getenv("SECRET_KEY", "bad")'))['pass'])
    def test_import_and_exec_rejected(self):
        self.assertFalse(scan('import subprocess\ndef validate_email(email):\n return bool(email)')['pass'])
        self.assertFalse(scan('def validate_email(email):\n return eval(email)')['pass'])
    def test_real_qa(self):
        result=qa(GOOD);self.assertTrue(result['pass'],result);self.assertEqual(len(result['cases']),14)
        self.assertFalse(qa('def validate_email(email):\n return "@" in email')['pass'])
    def test_unsupported_code_not_executed(self):
        with tempfile.TemporaryDirectory() as d:
            marker=Path(d)/'marker.txt'
            code=f'open({str(marker)!r},"w").write("bad")\ndef validate_email(email):\n return True'
            self.assertFalse(qa(code)['pass']);self.assertFalse(marker.exists())

class ScheduleTests(unittest.TestCase):
    def test_valid(self):self.assertTrue(validate_schedule(validate_tasks(TASKS),SCHEDULE)['valid'])
    def mutate(self,fn):
        data=json.loads(json.dumps(SCHEDULE));fn(data);self.assertFalse(validate_schedule(TASKS['tasks'],data)['valid'])
    def test_overlap(self):self.mutate(lambda x:x['schedule'][1].update(start_time=0,end_time=3))
    def test_missing(self):self.mutate(lambda x:x['schedule'].pop())
    def test_duplicate(self):self.mutate(lambda x:x['schedule'].append(x['schedule'][0]))
    def test_wrong_duration(self):self.mutate(lambda x:x['schedule'][0].update(end_time=1))
    def test_wrong_machine(self):self.mutate(lambda x:x['schedule'][0].update(machine='Sơn'))
    def test_precedence(self):self.mutate(lambda x:x['schedule'][3].update(start_time=0,end_time=2))
    def test_wrong_makespan(self):self.mutate(lambda x:x.update(makespan=1))
    def test_nonfinite(self):self.mutate(lambda x:x['schedule'][0].update(end_time=float('inf')))
    def test_boolean_duration_rejected(self):
        with self.assertRaises(ValueError):validate_tasks({'tasks':[{'id':'A','steps':[{'machine':'M','duration':True}]}]})

class PipelineTests(unittest.TestCase):
    def test_hub_block_repair_review(self):
        model=FakeModel();s=initial('hub','Implement a simple email validation function.')
        for _ in range(3):s=advance(s,model)
        self.assertEqual(s['phase'],'blocked');self.assertTrue(s['qa']['pass']);self.assertFalse(s['governance']['pass'])
        s=advance(s,model);self.assertIsNone(s['qa']);s=advance(s,model);self.assertEqual(s['phase'],'review')
        with self.assertRaises(ValueError):advance(s,model)
        s=advance(s,model,True);self.assertEqual(s['status'],'accepted')
    def test_mans_confirmation_and_repair(self):
        model=FakeModel(True);s=initial('mans','A needs cut 3 paint 2; B needs cut 2 paint 4.')
        for _ in range(3):s=advance(s,model)
        self.assertEqual(s['phase'],'verified')
        with self.assertRaises(ValueError):advance(s,model)
        s=advance(s,model,True);self.assertEqual(s['phase'],'invalid');self.assertFalse(s['validation']['valid'])
        s=advance(s,model);self.assertEqual(s['status'],'complete');self.assertEqual(s['validation']['makespan'],8)
    def test_clarification_blocks_architect(self):
        class Ask(FakeModel):
            def call(self,role,instruction,payload):
                if role=='verifier':return {'needs_clarification':True,'questions':['Thiếu thời lượng B']},{'role':role}
                return super().call(role,instruction,payload)
        m=Ask();s=initial('mans','A has cut 3; B has missing durations.')
        for _ in range(3):s=advance(s,m)
        self.assertEqual(s['status'],'clarification')
        with self.assertRaises(ValueError):advance(s,m,True)
    def test_failure_preserves_input_state(self):
        class Broken:
            def call(self,*_):raise ModelError('quota')
        s=initial('hub','Implement email validation function please.')
        with self.assertRaises(ModelError):advance(s,Broken())
        self.assertEqual(s['phase'],'ready');self.assertEqual(s['version'],0)
    def test_retry_cap(self):
        m=FakeModel(True);s=initial('mans','A and B need cutting and painting scheduling.')
        for _ in range(3):s=advance(s,m)
        for _ in range(3):
            s=advance(s,m,True);s['phase']='invalid';s['status']='blocked'
        n=len(m.calls);s=advance(s,m);self.assertEqual(s['status'],'exhausted');self.assertEqual(len(m.calls),n)

class HttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.model=FakeModel();self.server=make_server(0,self.model,Store(self.tmp.name));self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.base='http://127.0.0.1:'+str(self.server.server_address[1]);self.config=self.request('/api/config')
    def tearDown(self):self.server.shutdown();self.server.server_close();self.tmp.cleanup()
    def request(self,path,data=None,token='',app=True,extra=None):
        headers={'X-App-Token':self.config['app_token'] if app and hasattr(self,'config') else '', 'X-Session-Token':token}
        if extra:headers.update(extra)
        body=None
        if data is not None:body=json.dumps(data).encode();headers['Content-Type']='application/json'
        req=urllib.request.Request(self.base+path,data=body,headers=headers)
        with urllib.request.urlopen(req,timeout=10) as response:return json.load(response)
    def test_config_never_exposes_key(self):
        with patch('config.settings',return_value={'key':'PRIVATE_TEST_KEY','model':'model'}):
            self.assertNotIn('PRIVATE_TEST_KEY',json.dumps(self.request('/api/config')))
    def test_files_are_not_exposed(self):
        for path in ['/.env','/app.py','/.state/sessions.sqlite3','/../config.py']:
            with self.assertRaises(urllib.error.HTTPError) as error:self.request(path)
            self.assertEqual(error.exception.code,404)
    def test_csrf_and_origin(self):
        with self.assertRaises(urllib.error.HTTPError) as error:self.request('/api/sessions',{},app=False)
        self.assertEqual(error.exception.code,403)
        with self.assertRaises(urllib.error.HTTPError) as error:self.request('/api/sessions',{},extra={'Origin':'https://evil.example'})
        self.assertEqual(error.exception.code,403)
    def test_token_and_version(self):
        created=self.request('/api/sessions',{'kind':'hub','description':'Implement a basic email validation function.'});s=created['session'];token=created['session_token']
        with self.assertRaises(urllib.error.HTTPError):self.request('/api/next',{'id':s['id'],'version':0},token='wrong')
        updated=self.request('/api/next',{'id':s['id'],'version':0},token)['session'];self.assertEqual(updated['phase'],'planned')
        with self.assertRaises(urllib.error.HTTPError) as error:self.request('/api/next',{'id':s['id'],'version':0},token)
        self.assertEqual(error.exception.code,409)
    def test_local_gate_uses_no_llm(self):
        result=self.request('/api/gate',{'code':BAD});self.assertFalse(result['accepted']);self.assertTrue(result['qa']['pass']);self.assertEqual(self.model.calls,[])

if __name__=='__main__':unittest.main()
