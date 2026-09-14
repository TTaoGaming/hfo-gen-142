// Projection into the existing DO, R2 and NativeJobWorkflow; no scheduler.
const WORK_CELL_ID='gen142-work-cell-20260914-r1';
const WORK_CELL_INPUT_ID='gen142-work-cell-input-20260914-r1';
const WORK_CELL_INPUT_R2='gen142-work-cell-input-20260914-r2';
const WORK_CELL_KEY=WORK_CELL_ID+'/mission';
const WORK_CELL_BUDGET=WORK_CELL_ID+'/calls';
const WORK_CELL_ADMIT_BEFORE='2026-09-14T07:00:00Z';
const WORK_CELL_PARENT='8ed8148be615d06c4bf37bf8fe5715248923486b93ab36d2d49b3d503b9da517';
const workCanonical=x=>Array.isArray(x)?'['+x.map(workCanonical).join(',')+']':x!==null&&typeof x==='object'?'{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+workCanonical(x[k])).join(',')+'}':JSON.stringify(x);
const workBytes=x=>new TextEncoder().encode(x).byteLength;
function workAssert(ok,reason){if(!ok)throw Error(reason);}
async function workCellJson(request){
 workAssert(request.body,'EMPTY_BODY');const reader=request.body.getReader();const chunks=[];let length=0;
 try{for(;;){const {done,value}=await reader.read();if(done)break;length+=value.byteLength;if(length>32768){await reader.cancel();throw Error('INPUT_BYTES');}chunks.push(value);}}finally{reader.releaseLock();}
 const bytes=new Uint8Array(length);let at=0;for(const chunk of chunks){bytes.set(chunk,at);at+=chunk.byteLength;}
 return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
}

// Independent exact integer checker; candidate code never runs on this principal.
function workVerifyPacking(text){
 workAssert(typeof text==='string'&&workBytes(text)<=24000,'ARTIFACT_BOUND');
 const lines=text.trimEnd().split(/\r?\n/);workAssert(lines.length===121&&lines[1].length<=512,'PACKING_SHAPE');
 const scale=10n**18n;
 const number=s=>{workAssert(/^-?\d{1,2}(?:\.\d{1,18})?$/.test(s),'DECIMAL_SHAPE');const sign=s[0]==='-'?-1n:1n;const [a,b='']=s.replace(/^-/,'').split('.');return sign*(BigInt(a)*scale+BigInt(b.padEnd(18,'0')));};
 const r=number(lines[0]);workAssert(r>0n&&r<scale,'RADIUS_BOUND');
 const points=lines.slice(2).map(line=>{const p=line.trim().split(/\s+/).map(number);workAssert(p.length===6,'DIMENSION');return p;});
 const square=x=>x*x;let pairs=0;
 for(let i=0;i<points.length;i++){
  workAssert(points[i].reduce((s,x)=>s+square(x),0n)<=square(scale-r),'CONTAINMENT');
  for(let j=0;j<i;j++){workAssert(points[i].reduce((s,x,k)=>s+square(x-points[j][k]),0n)>=4n*square(r),'OVERLAP');pairs++;}
 }
 workAssert(r>=309963933216626000n,'REGRESSION');
 return {radius:lines[0],winner:r>309963943216626000n,containment_checks:119,pair_checks:pairs,scale_digits:18,verifier:'cloudflare-integer-geometry-v1'};
}

async function workCell(cell,env,action,input,workId=WORK_CELL_ID){
 workAssert([WORK_CELL_ID,WORK_CELL_INPUT_ID,WORK_CELL_INPUT_R2].includes(workId),'WORK_NOT_ADMITTED');
 const inputOnly=workId!==WORK_CELL_ID;
 const WORK_CELL_KEY=workId+'/mission',WORK_CELL_BUDGET=workId+'/calls';
 const get=()=>cell.ctx.storage.get(WORK_CELL_KEY);
 const save=async s=>{await cell.ctx.storage.put(WORK_CELL_KEY,s);await env.CELL_STATE.put(WORK_CELL_KEY+'.json',JSON.stringify(s));};
 // Catch expected refusals inside the gate: escaping a DO gate resets the actor.
 const gate=async fn=>{let answer,error;await cell.ctx.blockConcurrencyWhile(async()=>{try{answer=await fn();}catch(e){error=e;}});if(error)throw error;return answer;};
 const status=async()=>{
  const s=await get();if(!s)return {state:'NOT_ADMITTED',work_id:workId};
  const budget=await pdsaBudget(cell,env,null,WORK_CELL_BUDGET);
  return {...s,input_rows:(s.input_rows??[]).map(({response,...row})=>row),budget:{state:budget.state,deadline_ms:budget.deadline_ms,rows:(budget.rows??[]).map(({response,...row})=>row)},native:s.workflow?await env.NATIVE_JOBS.status({job_id:workId}):null};
 };
 if(action==='status')return status();
 if(action==='stop'){
  const result=await pdsaBudget(cell,env,'stop',WORK_CELL_BUDGET);
  await gate(async()=>{const s=await get();if(s){s.state='STOPPED';await save(s);}});return result;
 }
 if(action==='admit'){
  workAssert(input?.abi==='gen142.hatchery/0'&&input.work_id===workId&&input.profile==='packing.recipe.v1','WORKLOAD_PROFILE');
  workAssert(workCanonical(input.limits)===workCanonical({provider_requests:inputOnly?0:2,max_usd:0,lifetime_seconds:600,generations:2}),'CAP_BINDING');
  if(inputOnly)workAssert(input.proposal_source==='admitted-input'&&Array.isArray(input.context?.proposals)&&input.context.proposals.length===2&&input.context.proposals.every(p=>typeof p==='string'&&workBytes(p)<=4096)&&input.context.proposals[0]!==input.context.proposals[1],'INPUT_PROPOSALS');
  const context=workCanonical(input.context);
  workAssert(workBytes(context)<=16384&&await vpsHash(context)===input.context_sha256,'CONTEXT_HASH');
  workAssert(input.context?.parent_sha256===WORK_CELL_PARENT&&/^[a-f0-9]{64}$/.test(input.context.evaluator_sha256),'TASK_BINDING');
  const manifestHash=await vpsHash(workCanonical(input));let fresh=false;
  await gate(async()=>{
   const old=await get();if(old){workAssert(old.manifest_sha256===manifestHash,'WORK_ID_CONFLICT');return;}
   workAssert(Date.now()<Date.parse(WORK_CELL_ADMIT_BEFORE),'ADMISSION_EXPIRED');
   const legacy=await cell.ctx.storage.get(PDSA_KEY);workAssert(!legacy||legacy.state!=='RUNNING','LEGACY_ACTIVE');
   const s={work_id:workId,state:'START_RESERVED',manifest:input,manifest_sha256:manifestHash,context_ref:'work-cell/context/'+input.context_sha256,generations:[],input_rows:[],started_ms:Date.now(),deadline_ms:Date.now()+600000};
   await env.CELL_STATE.put(s.context_ref,context);await save(s);fresh=true;
  });
  if(!fresh)return status();
  const s=await get();
  const task={content:workCanonical({abi:input.abi,profile:input.profile,context_ref:s.context_ref,context_sha256:input.context_sha256,manifest_sha256:manifestHash,generations:2}),effect_ceiling:'NONE',output_max_bytes:16000};
  const request={job_id:workId,task,task_sha256:await vpsHash(workCanonical(task)),worker:{id:'oracle-packing-adapter',role:'native-worker'},adjudicator:{id:'cloudflare-integer-geometry',role:'independent-adjudicator'}};
  request.request_sha256=await vpsHash(workCanonical(request));
  await gate(async()=>{const row=await get();row.request=request;await save(row);});
  // start() reconciles its native Agent tracking row. An uncertain create is held.
  const workflow=await env.NATIVE_JOBS.start(request);
  await gate(async()=>{const row=await get();workAssert(row.state==='START_RESERVED','STOPPED_DURING_ADMISSION');row.workflow=workflow;row.state='RUNNING';await save(row);await cell.ctx.storage.put(WORK_CELL_BUDGET,{state:'RUNNING',started_ms:row.started_ms,deadline_ms:row.deadline_ms,rows:[],retries:0,max_calls:inputOnly?0:2});});
  return status();
 }
 if(action==='model'){
  const budget=await pdsaBudget(cell,env,null,WORK_CELL_BUDGET);
  const rows=inputOnly?(await get())?.input_rows:budget.rows;
  const requestHash=await vpsHash(JSON.stringify(input));const replay=rows?.find(r=>r.input_sha256===requestHash);
  if(replay)return replay.response??{error:{message:'PENDING_NO_RETRY'}};
  let admittedResponse;
  await gate(async()=>{
   const s=await get();workAssert(s?.state==='RUNNING'&&Date.now()<s.deadline_ms,'MISSION_NOT_RUNNING');
   const count=inputOnly?s.input_rows.length:(budget.rows?.length??0);
   workAssert(s.generations.length===count,'PREVIOUS_RESULT_NOT_VERIFIED');
   workAssert(count<2,'PROPOSAL_BUDGET');
   workAssert(input?.model==='packing-cell'&&Array.isArray(input.messages)&&input.messages.length>=2&&input.messages[0].role==='system','MODEL_SHAPE');
   const prefix=workCanonical(input.messages[0]),delta=workCanonical(input.messages.slice(1));
   workAssert(workBytes(prefix)<=16384&&workBytes(delta)<=16000,'CONTEXT_BOUND');
   const hash=await vpsHash(prefix);
   if(s.model_context_sha256)workAssert(s.model_context_sha256===hash,'MODEL_CONTEXT_CHANGED');
   else{await env.CELL_STATE.put('work-cell/context/'+hash,prefix);s.model_context_sha256=hash;}
   s.context_use_count=(s.context_use_count??0)+1;s.last_delta_sha256=await vpsHash(delta);s.last_delta_bytes=workBytes(delta);
   if(inputOnly){
    admittedResponse={id:workId+'-input-'+count,object:'chat.completion',created:Math.floor(Date.now()/1000),model:'admitted-input',choices:[{index:0,finish_reason:'stop',message:{role:'assistant',content:s.manifest.context.proposals[count]}}],usage:{prompt_tokens:0,completion_tokens:0,total_tokens:0}};
    s.input_rows.push({slot:count,source:'admitted-input',state:'INPUT_RETURNED',input_sha256:requestHash,proposal_sha256:await vpsHash(s.manifest.context.proposals[count]),response:admittedResponse,returned_utc:new Date().toISOString()});
   }
   await save(s);
  });
  if(inputOnly)return admittedResponse;
  return pdsaBudget(cell,env,input,WORK_CELL_BUDGET);
 }
 if(action==='generation'){
  workAssert(Number.isInteger(input?.generation)&&input.generation>=1&&input.generation<=2,'GENERATION_BOUND');
  const proof=workVerifyPacking(input.content);const artifactHash=await vpsHash(input.content);
  workAssert(input.metrics?.reason==='COMPLETE'&&input.metrics.trial_count===8&&/^[a-f0-9]{64}$/.test(input.program_sha256),'EVALUATION_INCOMPLETE');
  const digest=await vpsHash(workCanonical(input));
  return gate(async()=>{
   const s=await get();workAssert(s,'NOT_ADMITTED');
   const prior=s.generations.find(g=>g.generation===input.generation);
   if(prior){workAssert(prior.submission_sha256===digest,'GENERATION_CONFLICT');return {accepted:true,replayed:true,receipt:prior};}
   workAssert(['RUNNING','STOPPED'].includes(s.state)&&Date.now()<s.deadline_ms,'MISSION_NOT_RUNNING');
   workAssert(input.generation===s.generations.length+1,'GENERATION_ORDER');
   const budget=await cell.ctx.storage.get(WORK_CELL_BUDGET);
   workAssert(inputOnly?s.input_rows[input.generation-1]?.state==='INPUT_RETURNED':budget?.rows[input.generation-1]?.state==='RETURNED','PROPOSAL_NOT_RETURNED');
   const artifact_ref='work-cell/artifact/'+artifactHash;
   await env.CELL_STATE.put(artifact_ref,input.content);
   const metrics={reason:input.metrics.reason,trial_count:input.metrics.trial_count,radius:proof.radius,winner:proof.winner};
   const receipt={generation:input.generation,program_sha256:input.program_sha256,artifact_sha256:artifactHash,artifact_ref,submission_sha256:digest,proof,metrics,verified_utc:new Date().toISOString()};
   s.generations.push(receipt);s.memory={last_verified_generation:input.generation,best_artifact_sha256:artifactHash,last_result:metrics};await save(s);
   return {accepted:true,receipt};
  });
 }
 if(action==='finish'||action==='fail'){
  const failed=action==='fail';
  if(failed){workAssert(['PROVIDER_HOLD','CALLER_FAILED','EVALUATION_REJECTED','DEADLINE'].includes(input?.reason),'FAILURE_CLASS');await pdsaBudget(cell,env,'stop',WORK_CELL_BUDGET);}
  let result;
  await gate(async()=>{
   const s=await get();workAssert(s?.request,'NOT_ADMITTED');
   if(!failed)workAssert(s.generations.length===2||s.generations.some(g=>g.proof.winner),'TWO_VERIFIED_GENERATIONS_REQUIRED');
   if(s.result){result=s.result;return;}
   workAssert(['RUNNING','STOPPED'].includes(s.state)&&(failed||Date.now()<s.deadline_ms),'MISSION_NOT_RUNNING');
   if(failed)s.failure=input.reason;
   const content=workCanonical({work_id:workId,context_sha256:s.manifest.context_sha256,generations:s.generations,memory:s.memory??null,failure:s.failure??null});
   result={job_id:workId,task_sha256:s.request.task_sha256,worker_id:s.request.worker.id,adjudicator_id:s.request.adjudicator.id,output_sha256:await vpsHash(content),evidence_sha256:await vpsHash(workCanonical(s.generations)),verdict:failed?'reject':'accept',content,detail:failed?'Work failed: '+input.reason:`${s.generations.length} native numerical evaluations; exact integer geometry checked on Cloudflare outside candidate runtime.`};
   s.result=result;s.state='RESULT_RESERVED';await save(s);
  });
  // Native workflow validates identity/content hashes; identical event replay has
  // no provider or numerical effect. No caller-side inference retry is introduced.
  const native=await env.NATIVE_JOBS.status({job_id:workId});
  if(native?.status!=='complete'&&native?.status!=='completed')await env.NATIVE_JOBS.submit({job_id:workId,result});
  await gate(async()=>{const s=await get();s.state='RESULT_SUBMITTED';await save(s);});
  await pdsaBudget(cell,env,'stop',WORK_CELL_BUDGET);return status();
 }
 throw Error('UNSUPPORTED_ACTION');
}
