import unittest
from server import run_pipeline, parse_json

class PipelineTests(unittest.TestCase):
    def test_architect_receives_verified_correction(self):
        calls=[]
        def fake(role,payload):
            calls.append((role,payload))
            if role=='seeker': return {'tasks':[{'id':'A'}]}
            if role=='weaver': return {'tasks':[{'id':'A','steps':[{'machine':'M','duration':9}]}]}
            if role=='verified': return {'tasks':[{'id':'A','steps':[{'machine':'M','duration':3}]}]}
            self.assertEqual(payload['verified']['tasks'][0]['steps'][0]['duration'],3)
            return {'schedule':[{'task_id':'A','step_id':1,'machine':'M','start_time':0,'end_time':3}]}
        run_pipeline('A needs machine M for three minutes.',fake)
        self.assertEqual([r for r,_ in calls],['seeker','weaver','verified','architect'])

    def test_invalid_input_does_not_call_api(self):
        with self.assertRaises(ValueError): run_pipeline('short',lambda *_:self.fail('API called'))

    def test_markdown_json(self):
        self.assertEqual(parse_json('```json\n{"tasks": []}\n```'),{'tasks':[]})

if __name__=='__main__': unittest.main()
