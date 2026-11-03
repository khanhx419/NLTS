import math

def number(value):return type(value) in (int,float) and math.isfinite(value)

# Kiểm tra cấu trúc dữ liệu; chưa chứng minh dữ liệu khớp văn bản gốc.
def validate_tasks(data):
    if not isinstance(data,dict):raise ValueError('Cấu trúc công việc phải là object.')
    tasks=data.get('tasks')
    if not isinstance(tasks,list) or not 1<=len(tasks)<=8:raise ValueError('Phạm vi demo: 1–8 nhiệm vụ.')
    ids=set();count=0
    for t in tasks:
        if not isinstance(t,dict) or not isinstance(t.get('id'),str) or not 1<=len(t['id'])<=40 or t['id'] in ids:raise ValueError('Mã nhiệm vụ phải là chuỗi duy nhất, tối đa 40 ký tự.')
        ids.add(t['id'])
        if not isinstance(t.get('steps'),list) or not 1<=len(t['steps'])<=12:raise ValueError('Mỗi nhiệm vụ cần 1–12 công đoạn.')
        count+=len(t['steps'])
        for s in t['steps']:
            if not isinstance(s,dict) or not isinstance(s.get('machine'),str) or not 1<=len(s['machine'])<=60:raise ValueError('Mỗi công đoạn cần tên máy/tài nguyên tối đa 60 ký tự.')
            if not number(s.get('duration')) or not 0<s['duration']<=10000:raise ValueError('Thời lượng phải là số dương, tối đa 10.000 đơn vị.')
    if count>36:raise ValueError('Tối đa 36 công đoạn để hạn chế token API.')
    return tasks

# Kiểm tra lịch độc lập với LLM: đủ bước, thời lượng, thứ tự và tài nguyên.
# Hợp lệ không có nghĩa đã chứng minh tối ưu.
def validate_schedule(tasks,result):
    expected={(t['id'],i+1):op for t in tasks for i,op in enumerate(t['steps'])}
    schedule=result.get('schedule') if isinstance(result,dict) else None
    if not isinstance(schedule,list) or not schedule or len(schedule)>72:return {'valid':False,'errors':['Không có danh sách công đoạn hợp lệ.'],'makespan':None,'checks':{}}
    errors=[];seen={};valid_times=[]
    checks={'complete':True,'durations':True,'precedence':True,'resources':True,'times':True}
    for row in schedule:
        if not isinstance(row,dict):errors.append('Có dòng lịch không phải object.');checks['complete']=False;continue
        task,step=row.get('task_id'),row.get('step_id')
        if not isinstance(task,str) or type(step) is not int:errors.append('Dòng lịch thiếu task_id hoặc step_id nguyên.');checks['complete']=False;continue
        key=(task,step);label=f'{task}.{step}'
        if key not in expected:errors.append('Công đoạn không có trong dữ liệu đã xác nhận: '+label);checks['complete']=False;continue
        if key in seen:errors.append('Công đoạn bị lặp: '+label);checks['complete']=False
        seen[key]=row
        start,end=row.get('start_time'),row.get('end_time')
        if not number(start) or not number(end) or start<0 or end<=start or end>1000000:
            errors.append('Khoảng thời gian không hợp lệ: '+label);checks['times']=False;continue
        valid_times.append(row)
        if abs(end-start-expected[key]['duration'])>1e-7:errors.append('Sai thời lượng: '+label);checks['durations']=False
        if row.get('machine')!=expected[key]['machine']:errors.append('Sai tài nguyên: '+label);checks['resources']=False
    for key in expected:
        if key not in seen:errors.append(f'Thiếu công đoạn: {key[0]}.{key[1]}');checks['complete']=False
    for t in tasks:
        for i in range(1,len(t['steps'])):
            a,b=seen.get((t['id'],i)),seen.get((t['id'],i+1))
            if a in valid_times and b in valid_times and b['start_time']<a['end_time']-1e-7:
                errors.append(f'Sai thứ tự: {t["id"]}.{i+1} bắt đầu trước khi bước {i} xong.');checks['precedence']=False
    for i,a in enumerate(valid_times):
        for b in valid_times[i+1:]:
            if a.get('machine')==b.get('machine') and max(a['start_time'],b['start_time'])<min(a['end_time'],b['end_time'])-1e-7:
                errors.append(f'Trùng tài nguyên {a.get("machine")}: {a["task_id"]}.{a["step_id"]} và {b["task_id"]}.{b["step_id"]}.');checks['resources']=False
    makespan=max((r['end_time'] for r in valid_times),default=None)
    reported=result.get('makespan')
    if reported is not None and (not number(reported) or makespan is None or abs(reported-makespan)>1e-7):errors.append('Makespan model khai báo không khớp lịch.');checks['times']=False
    return {'valid':not errors,'errors':errors[:100],'makespan':makespan,'checks':checks}
