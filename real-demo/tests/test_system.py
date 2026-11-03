import sys,json,unittest,tempfile,threading,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scheduling import validate_tasks,validate_schedule
from pipeline import initial,advance
from store import Store
from app import make_server
from llm import Gemini,ModelError

TASKS={'tasks':[{'id':'A','name':'A','steps':[{'machine':'Cắt','duration':3},{'machine':'Sơn','duration':2}]},{'id':'B','name':'B','steps':[{'machine':'Cắt','duration':2},{'machine':'Sơn','duration':4}]}],'unit':'phút','changes':[],'needs_clarification':False}
SCHEDULE={'schedule':[{'task_id':'B','step_id':1,'machine':'Cắt','start_time':0,'end_time':2},{'task_id':'A','step_id':1,'machine':'Cắt','start_time':2,'end_time':5},{'task_id':'B','step_id':2,'machine':'Sơn','start_time':2,'end_time':6},{'task_id':'A','step_id':2,'machine':'Sơn','start_time':6,'end_time':8}],'makespan':8}

class FakeModel:
    def __init__(self,bad_schedule=False):self.calls=[];self.bad_schedule=bad_schedule;self.dev_calls=0
    def call(self,role,instruction,payload):
        self.calls.append((role,payload))
        if role=='seeker':data={'tasks':[{'id':'A','name':'A'},{'id':'B','name':'B'}]}
        elif role in ('weaver','verifier'):data=json.loads(json.dumps(TASKS))
        else:
            assert payload['verified']['tasks']==TASKS['tasks']
            data=json.loads(json.dumps(SCHEDULE))
            if self.bad_schedule and 'trusted_feedback' not in payload:data['schedule'][1]['start_time']=0
        return data,{'role':role,'provider':'TEST DOUBLE','model':'fake','seconds':0,'input_tokens':1,'output_tokens':1}


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
        s=initial('mans','Schedule two jobs from their steps please.')
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
        created=self.request('/api/sessions',{'kind':'mans','description':'A and B need cutting and painting scheduling.'});s=created['session'];token=created['session_token']
        with self.assertRaises(urllib.error.HTTPError):self.request('/api/next',{'id':s['id'],'version':0},token='wrong')
        updated=self.request('/api/next',{'id':s['id'],'version':0},token)['session'];self.assertEqual(updated['phase'],'sought')
        with self.assertRaises(urllib.error.HTTPError) as error:self.request('/api/next',{'id':s['id'],'version':0},token)
        self.assertEqual(error.exception.code,409)

if __name__=='__main__':unittest.main()
