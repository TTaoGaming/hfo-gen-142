// Finite authenticated assay over existing Gen141Cell + NATIVE_JOBS.
// No provider, arbitrary task, queue, cron or new durable namespace.
const HATCHERY_ASSAY_KEY='gen142-hatchery-g1-20260914-r1';
const HATCHERY_ASSAY_CONTENT='{"items":[{"count":1,"text":"applications"},{"count":1,"text":"evolution"},{"count":2,"text":"research"}],"total":4}';
async function hatcheryNativeAssay(cell,env,action,text=''){
 const state=await cell.ctx.storage.get(HATCHERY_ASSAY_KEY);
 if(action==='status'){
  const workflow=state?.workflow?await env.NATIVE_JOBS.status({job_id:HATCHERY_ASSAY_KEY}):null;
  return {receipt:state??null,workflow};
 }
 if(Date.now()>=Date.parse('2026-09-14T03:00:00Z'))return {state:'DEADLINE_HOLD'};
 if(action==='start'){
  let acquired=false;
  await cell.ctx.blockConcurrencyWhile(async()=>{
   if(await cell.ctx.storage.get(HATCHERY_ASSAY_KEY))return;
   await cell.ctx.storage.put(HATCHERY_ASSAY_KEY,{state:'START_RESERVED',accepted_effect_count:0,utc:new Date().toISOString()});acquired=true;
  });
  if(!acquired)return {state:'EXISTS_NO_RESTART'};
  const task={content:'Reduce the fixed bootstrap fixture; expected canonical output is '+HATCHERY_ASSAY_CONTENT,effect_ceiling:'NONE',output_max_bytes:1024};
  const request={job_id:HATCHERY_ASSAY_KEY,task,task_sha256:await vpsHash(vpsCanonical(task)),worker:{id:'portable-hatchery-assay',role:'native-worker'},adjudicator:{id:'fixed-output-oracle',role:'independent-adjudicator'}};
  request.request_sha256=await vpsHash(vpsCanonical(request));
  const row={state:'CHECKPOINT_RESERVED',request,accepted_effect_count:0,checkpoint:1};
  await cell.ctx.storage.put(HATCHERY_ASSAY_KEY,row);
  row.workflow=await env.NATIVE_JOBS.start(request);row.state='WAITING_REPLACEMENT';
  await cell.ctx.storage.put(HATCHERY_ASSAY_KEY,row);
  await env.CELL_STATE.put(HATCHERY_ASSAY_KEY+'.json',JSON.stringify(row));
  return {state:row.state,work_id:HATCHERY_ASSAY_KEY,checkpoint:1};
 }
 if(action!=='submit'||text!==HATCHERY_ASSAY_CONTENT)return {state:'CONFLICT_REJECTED'};
 let row,acquired=false;
 await cell.ctx.blockConcurrencyWhile(async()=>{
  row=await cell.ctx.storage.get(HATCHERY_ASSAY_KEY);
  if(row?.state!=='WAITING_REPLACEMENT')return;
  row.state='EFFECT_RESERVED';row.output_sha256=await vpsHash(text);
  await cell.ctx.storage.put(HATCHERY_ASSAY_KEY,row);acquired=true;
 });
 if(!acquired)return {state:row?.state??'NO_START',replayed:true};
 const result={job_id:HATCHERY_ASSAY_KEY,task_sha256:row.request.task_sha256,worker_id:row.request.worker.id,adjudicator_id:row.request.adjudicator.id,output_sha256:row.output_sha256,evidence_sha256:await vpsHash('fixed-output-exact-equality-v1'),verdict:'accept',content:text,detail:'Exact immutable fixture checked by bridge; caller replacement assay, not independent model review.'};
 row.result=result;await cell.ctx.storage.put(HATCHERY_ASSAY_KEY,row);
 await env.NATIVE_JOBS.submit({job_id:HATCHERY_ASSAY_KEY,result});
 row.state='RESULT_SUBMITTED';row.accepted_effect_count=1;
 row.consumer_ack={consumer:'fixed-output-oracle',output_sha256:row.output_sha256,verdict:'accepted',utc:new Date().toISOString()};
 await cell.ctx.storage.put(HATCHERY_ASSAY_KEY,row);
 await env.CELL_STATE.put(HATCHERY_ASSAY_KEY+'.json',JSON.stringify(row));
 return {state:row.state,accepted_effect_count:row.accepted_effect_count};
}
