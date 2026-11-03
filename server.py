"""Local static server and four-role MANS-inspired pipeline. Python 3.10+, stdlib only."""
import json
import os
import re
import math
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROMPTS = {
    'seeker': 'You are Seeker. Extract every task and its quantity from the original description. Do not invent work. Return JSON {"tasks":[{"id":"A","name":"..."}]}.',
    'weaver': 'You are Weaver. Extract ordered steps for every task. Each step requires one named machine and a positive numeric duration. Preserve machine names exactly. Return JSON {"tasks":[{"id":"A","steps":[{"machine":"Cắt","duration":3}]}]}. Steps are sequential and non-preemptive. Do not schedule yet.',
    'verified': 'You are Verifier. Check extracted tasks, quantities, ordered steps, machine names and durations against the original description. Correct omissions and mistakes. Do not invent facts. Return the corrected JSON {"tasks":[{"id":"A","steps":[{"machine":"Cắt","duration":3}]}]}.',
    'architect': 'You are Architect. Schedule ALL verified tasks. Minimize makespan while respecting ordered steps, exact durations, and capacity 1 per machine. Analyze bottlenecks and allow strategic idle time. Use task IDs, step numbers starting at 1, and machine names exactly as verified. Return JSON {"schedule":[{"task_id":"A","step_id":1,"machine":"Cắt","start_time":0,"end_time":3}],"makespan":3}. Return JSON only.',
}

def parse_json(text):
    text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip())
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError('Model phải trả về một JSON object.')
    return value

def call_model(role, payload):
    key = os.getenv('LLM_API_KEY', '')
    base = os.getenv('LLM_BASE_URL', '').rstrip('/')
    model = os.getenv('LLM_MODEL', '')
    if not key or not base or not model:
        raise ValueError('Thiếu LLM_API_KEY, LLM_BASE_URL hoặc LLM_MODEL trên server.')
    req = urllib.request.Request(base + '/chat/completions', data=json.dumps({
        'model': model,
        'messages': [{'role':'system','content':PROMPTS[role]}, {'role':'user','content':json.dumps(payload, ensure_ascii=False)}],
    }).encode(), headers={'Authorization':'Bearer '+key, 'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return parse_json(json.load(response)['choices'][0]['message']['content'])
    except urllib.error.HTTPError as error:
        raise ValueError(f'LLM API trả HTTP {error.code}; kiểm tra model, endpoint và quyền truy cập.') from None

def validate_tasks(data):
    tasks = data.get('tasks')
    if not isinstance(tasks,list) or not 1 <= len(tasks) <= 12:
        raise ValueError('Verifier phải trả 1–12 nhiệm vụ.')
    ids=set()
    for task in tasks:
        if not isinstance(task,dict) or not isinstance(task.get('id'),str) or not task['id'] or task['id'] in ids:
            raise ValueError('Task ID phải là chuỗi không rỗng và duy nhất.')
        ids.add(task['id'])
        if not isinstance(task.get('steps'),list) or not 1 <= len(task['steps']) <= 20:
            raise ValueError('Mỗi nhiệm vụ phải có 1–20 bước.')
        for step in task['steps']:
            if not isinstance(step,dict) or not isinstance(step.get('machine'),str) or not step['machine']:
                raise ValueError('Mỗi bước cần tên máy.')
            duration=step.get('duration')
            if type(duration) not in (int,float) or not math.isfinite(duration) or duration<=0:
                raise ValueError('Thời lượng bước phải dương và hữu hạn.')

def run_pipeline(description, caller=call_model):
    if not isinstance(description,str) or not 20 <= len(description) <= 12000:
        raise ValueError('Mô tả cần từ 20 đến 12.000 ký tự.')
    seeker=caller('seeker',{'description':description})
    weaver=caller('weaver',{'description':description,'tasks':seeker})
    verified=caller('verified',{'description':description,'extracted':weaver})
    validate_tasks(verified)
    result=caller('architect',{'description':description,'verified':verified})
    schedule=result.get('schedule')
    if not isinstance(schedule,list) or not 1 <= len(schedule) <= 240:
        raise ValueError('Architect không trả về lịch có cấu trúc phù hợp.')
    for s in schedule:
        if not isinstance(s,dict) or not isinstance(s.get('task_id'),str) or not isinstance(s.get('machine'),str) or type(s.get('step_id')) is not int:
            raise ValueError('Lịch thiếu task_id, machine hoặc step_id hợp lệ.')
        for field in ('start_time','end_time'):
            if type(s.get(field)) not in (int,float) or not math.isfinite(s[field]):
                raise ValueError('Lịch có giá trị thời gian không hợp lệ.')
    return dict(seeker=seeker,weaver=weaver,verified=verified,result=result)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)

    def send_json(self,status,value):
        data=json.dumps(value,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path!='/api/mans':
            return self.send_json(404,{'error':'Không có endpoint này.'})
        # No cross-origin calls; credentials stay on this machine.
        if self.headers.get('Host') not in ('127.0.0.1:8765','localhost:8765') or self.headers.get('Origin') not in (None,'http://127.0.0.1:8765','http://localhost:8765'):
            return self.send_json(403,{'error':'Chỉ chấp nhận yêu cầu từ giao diện trên máy.'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=60000:
                raise ValueError('Kích thước yêu cầu không hợp lệ.')
            request=json.loads(self.rfile.read(size))
            self.send_json(200,run_pipeline(request.get('description')))
        except (ValueError,KeyError,TypeError,urllib.error.URLError,TimeoutError):
            # No request payload, response body or credentials in error output.
            self.send_json(400,{'error':'Không chạy được pipeline. Kiểm tra biến môi trường, kết nối API và định dạng JSON/model đầu ra.'})

    def do_GET(self):
        # Do not expose dotfiles or local credentials through the static server.
        from urllib.parse import unquote, urlsplit
        parts=Path(unquote(urlsplit(self.path).path)).parts
        if any(p.startswith('.') for p in parts) or any(p.lower().endswith(('.env','.pem','.key')) for p in parts):
            self.send_error(403)
            return
        super().do_GET()

if __name__=='__main__':
    import sys,runpy
    real_root=Path(__file__).parent/'real-demo'
    sys.path.insert(0,str(real_root))
    runpy.run_path(str(real_root/'app.py'),run_name='__main__')
