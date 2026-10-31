(function(root){
function validate(tasks,schedule){
 const errors=[],expected=new Map(tasks.flatMap(t=>t.steps.map((s,i)=>[`${t.id}:${i+1}`,{...s,task:t.id,step:i+1}]))),seen=new Set();
 for(const s of schedule){let k=`${s.task_id}:${s.step_id}`,ref=expected.get(k);if(!ref){errors.push(`Bước không có trong yêu cầu: ${k}`);continue}if(seen.has(k))errors.push(`Bước bị lặp: ${k}`);seen.add(k);if(!Number.isFinite(s.start_time)||!Number.isFinite(s.end_time)||s.start_time<0||s.end_time<=s.start_time)errors.push(`Thời gian không hợp lệ: ${k}`);if(s.machine!==ref.machine)errors.push(`Sai máy: ${k}`);if(Math.abs((s.end_time-s.start_time)-ref.duration)>1e-8)errors.push(`Sai thời lượng: ${k}`);}
 for(const k of expected.keys())if(!seen.has(k))errors.push(`Thiếu bước: ${k}`);
 for(const t of tasks)for(let i=1;i<t.steps.length;i++){let prev=schedule.find(s=>s.task_id===t.id&&s.step_id===i),cur=schedule.find(s=>s.task_id===t.id&&s.step_id===i+1);if(prev&&cur&&cur.start_time<prev.end_time)errors.push(`Sai thứ tự: ${t.id} bước ${i+1}`)}
 for(let i=0;i<schedule.length;i++)for(let j=i+1;j<schedule.length;j++){let a=schedule[i],b=schedule[j];if(a.machine===b.machine&&Math.max(a.start_time,b.start_time)<Math.min(a.end_time,b.end_time))errors.push(`Trùng ${a.machine}: ${a.task_id}.${a.step_id} / ${b.task_id}.${b.step_id}`)}
 return {valid:errors.length===0,errors,makespan:schedule.length?Math.max(...schedule.map(s=>s.end_time)):0};
}
function solve(tasks){ // Exhaustive serial priority orders for the tiny teaching example.
 let best=null;
 function visit(done,mt,tt,sched){if(sched.length===tasks.reduce((n,t)=>n+t.steps.length,0)){let makespan=Math.max(...sched.map(s=>s.end_time));if(!best||makespan<best.makespan)best={schedule:sched,makespan};return}for(const t of tasks){let i=done[t.id]||0;if(i===t.steps.length)continue;let s=t.steps[i],start=Math.max(mt[s.machine]||0,tt[t.id]||0),end=start+s.duration;visit({...done,[t.id]:i+1},{...mt,[s.machine]:end},{...tt,[t.id]:end},[...sched,{task_id:t.id,step_id:i+1,machine:s.machine,start_time:start,end_time:end}])}}
 visit({},{},{},[]);return best;
}
const api={validate,solve};if(typeof module!=='undefined')module.exports=api;root.ScheduleEngine=api;
})(typeof globalThis!=='undefined'?globalThis:this);
