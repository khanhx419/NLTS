const assert=require('node:assert/strict');const {solve,validate}=require('./demo/engine.js');
const tasks=[{id:'A',steps:[{machine:'Cắt',duration:3},{machine:'Sơn',duration:2}]},{id:'B',steps:[{machine:'Cắt',duration:2},{machine:'Sơn',duration:4}]}];
const best=solve(tasks);assert.equal(best.makespan,8);assert.equal(validate(tasks,best.schedule).valid,true);
const bad=structuredClone(best.schedule);bad.find(s=>s.task_id==='A'&&s.step_id===1).start_time=0;assert.equal(validate(tasks,bad).valid,false);
assert.equal(validate(tasks,best.schedule.slice(1)).valid,false);
assert.equal(validate(tasks,[...best.schedule,best.schedule[0]]).valid,false);
console.log('PASS: optimum=8, feasible schedule, overlap, missing and duplicate steps');
