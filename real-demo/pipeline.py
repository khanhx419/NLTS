import copy
import time
from scheduling import validate_tasks,validate_schedule
from llm import ModelError

COMMON='The user is demonstrating a small real system. Do not fabricate a test result or say a checker passed. All checks run in separate trusted Python code. Explanations in Vietnamese, JSON keys as specified. '
PROMPTS={
 'seeker':COMMON+'''You are Seeker. Read a natural-language scheduling request. Extract ALL distinct tasks/jobs and their quantities. Expand repeated jobs to unique IDs. Return {"tasks":[{"id":"A","name":"..."}],"summary":"..."}. Do not schedule yet. Maximum 8 jobs. Never invent missing durations.''',
 'weaver':COMMON+'''You are Weaver. For every Seeker task, extract an ordered sequence of non-preemptive steps, each requiring ONE named machine/resource at capacity 1 and a positive numeric duration. Preserve task IDs, resource names and durations. Convert durations to a single declared unit. Return {"tasks":[{"id":"A","name":"...","steps":[{"machine":"Cắt","duration":3}]}],"unit":"phút","summary":"..."}. No scheduling, no invented facts. Missing/ambiguous details must be mentioned in summary.''',
 'verifier':COMMON+'''You are Verifier. Compare Weaver data against original request: check tasks/quantities, every step, order, resource name, duration, unit. Correct discrepancies. Return {"tasks":[{"id":"A","name":"...","steps":[{"machine":"Cắt","duration":3}]}],"unit":"phút","changes":["what changed"],"needs_clarification":false,"questions":[],"summary":"..."}. If information is missing or contradicts itself, set needs_clarification true with questions. Scope ONLY sequential steps within each job, each requiring one capacity-1 resource, start at time 0 or later. Set needs_clarification true for unsupported cross-job dependencies, due/release dates, resource calendars, multiple capacities or uncertain durations. Do not invent missing values or quietly ignore unsupported constraints. Do not schedule.''',
 'architect':COMMON+'''You are Architect. Produce a complete feasible schedule for the VERIFIED tasks. Follow their IDs, step order, machine names, exact positive durations. One machine handles at most one step at a time, steps cannot be interrupted, all times >=0. Aim to minimize makespan; identify bottlenecks, allow strategic idle time. Output {"schedule":[{"task_id":"A","step_id":1,"machine":"Cắt","start_time":0,"end_time":3}],"makespan":3,"summary":"..."}. Include EVERY step exactly once. Do not call an external solver, do not invent new work. If trusted validator feedback is present, correct the schedule to resolve ALL reported violations. Return the actual full revised schedule, not just an explanation. A feasible result is not a proof of optimality.'''
}

# Trạng thái chung của phiên: mỗi lần bấm chuyển đúng một bước.
def initial(kind,description,initial_code=''):
    if kind != 'mans':raise ValueError('Chọn MANS.')
    if not isinstance(description,str) or not 20<=len(description)<=10000:raise ValueError('Yêu cầu cần từ 20 đến 10.000 ký tự.')
    if not isinstance(initial_code,str) or len(initial_code)>12000:raise ValueError('Mã đầu vào quá dài.')
    return {'kind':kind,'description':description,'initial_code':initial_code,'phase':'ready','status':'ready',
            'seeker':None,'weaver':None,'verified':None,
            'result':None,'validation':None,'schedule_attempts':0,'events':[],'calls':[],'last_error':None,
            'created_at':time.time(),'version':0}

def event(s,actor,message):s['events'].append({'actor':actor,'message':message,'time':time.time()})

# Mỗi vai trò dùng prompt riêng nhưng có thể gọi chung một model Gemini.
def call(s,model,role,payload):
    data,meta=model.call(role,PROMPTS[role],payload)
    s['calls'].append(meta)
    if not isinstance(data,dict):raise ModelError('Kết quả agent không phải JSON object.')
    return data
# Coordinator: chọn vai trò theo trạng thái; confirmed là xác nhận người dùng.
def advance(state,model,confirmed=False):
    s=copy.deepcopy(state)
    if s['status'] in ('accepted','complete','exhausted','clarification'):raise ValueError('Phiên đã dừng. Tạo phiên mới để đổi yêu cầu.')
    if s['phase']=='ready':
        s['seeker']=call(s,model,'seeker',{'description':s['description']})
        tasks=s['seeker'].get('tasks')
        if not isinstance(tasks,list) or not 1<=len(tasks)<=8 or any(not isinstance(t,dict) or not isinstance(t.get('id'),str) or not isinstance(t.get('name'),str) for t in tasks):raise ModelError('Seeker không trả danh sách nhiệm vụ hợp lệ.')
        if len({t['id'] for t in tasks})!=len(tasks):raise ModelError('Seeker trả mã nhiệm vụ trùng.')
        s['phase']='sought';s['status']='running';event(s,'Seeker → Weaver','Gemini đã xác định nhiệm vụ từ văn bản.')
    elif s['phase']=='sought':
        s['weaver']=call(s,model,'weaver',{'description':s['description'],'seeker_tasks':s['seeker']['tasks']})
        validate_tasks(s['weaver']);s['phase']='woven';event(s,'Weaver → Verifier','Gemini đã trích xuất công đoạn, tài nguyên và thời lượng.')
    elif s['phase']=='woven':
        data=call(s,model,'verifier',{'description':s['description'],'extracted':s['weaver']})
        if type(data.get('needs_clarification')) is not bool:raise ModelError('Verifier thiếu cờ needs_clarification.')
        if data['needs_clarification']:
            if not isinstance(data.get('questions'),list) or not data['questions']:raise ModelError('Verifier cần chỉ rõ câu hỏi làm rõ.')
            s['verified']=data;s['phase']='clarification';s['status']='clarification';event(s,'Verifier → Người dùng','Thiếu thông tin hoặc yêu cầu ngoài phạm vi; cần sửa mô tả và tạo phiên mới.')
        else:
            validate_tasks(data)
            if not isinstance(data.get('unit'),str) or not 1<=len(data['unit'])<=30:raise ModelError('Verifier cần khai báo đơn vị thời gian.')
            s['verified']=data;s['phase']='verified';s['status']='review';event(s,'Verifier → Người dùng','Đối chiếu các công đoạn dưới đây với yêu cầu trước khi cho Architect lập lịch.')
    elif s['phase'] in ('verified','invalid'):
        if s['phase']=='verified' and not confirmed:raise ValueError('Cần xác nhận dữ liệu đã đối chiếu với mô tả gốc.')
        if s['schedule_attempts']>=3:s['status']='exhausted';event(s,'Coordinator','Dừng sau 3 lịch chưa đạt kiểm tra.')
        else:
            payload={'description':s['description'],'verified':s['verified']}
            if s['validation']:payload.update(previous_schedule=s['result'],trusted_feedback=s['validation'])
            data=call(s,model,'architect',payload)
            validation=validate_schedule(s['verified']['tasks'],data)
            s['result']=data;s['validation']=validation;s['schedule_attempts']+=1
            s['phase']='complete' if validation['valid'] else 'invalid';s['status']='complete' if validation['valid'] else 'blocked'
            event(s,'Architect → Bộ kiểm tra','Lịch đạt kiểm tra cục bộ.' if validation['valid'] else 'Lịch có vi phạm; giữ nguyên lỗi để yêu cầu Architect sửa.')
    else:raise ValueError('Trạng thái MANS không hợp lệ.')
    s['last_error']=None;s['version']+=1
    return s
