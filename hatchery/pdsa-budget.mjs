// Thin, finite OpenAI-compatible admission adapter for the installed Shinka engine.
// Existing DO owns the reservation; existing AI Gateway owns free-provider transport.
const PDSA_KEY='packing-shinka-pdsa-20260914-r1';
const PDSA_LANES=[['kimi','k3-256k'],['google-ai-studio','gemini-3.5-flash-lite'],['groq','openai/gpt-oss-120b'],['openrouter','nvidia/nemotron-3.5-lightning:free'],['kimi','k3-256k']];
async function pdsaBudget(cell,env,input){
 if(input===null)return await cell.ctx.storage.get(PDSA_KEY)??{state:'NOT_STARTED'};
 if(input==='stop'){
  let stopped=false;await cell.ctx.blockConcurrencyWhile(async()=>{const s=await cell.ctx.storage.get(PDSA_KEY);if(s){s.stop_requested=true;s.state='STOPPED_BY_EVALUATOR';await cell.ctx.storage.put(PDSA_KEY,s);await env.CELL_STATE.put(PDSA_KEY+'.json',JSON.stringify(s));stopped=true;}});return {stopped};
 }
 const serialized=JSON.stringify(input);
 if(serialized.length>32000||input.model!=='packing-cell'||!Array.isArray(input.messages)||input.messages.length>8)
  return {error:{message:'INPUT_HOLD'}};
 if(input.messages.some(m=>!['user','system','assistant'].includes(m.role)||typeof m.content!=='string'))return {error:{message:'MESSAGE_HOLD'}};
 const hash=await vpsHash(serialized);let acquired=false,s,row,existing;
 await cell.ctx.blockConcurrencyWhile(async()=>{
  s=await cell.ctx.storage.get(PDSA_KEY);
  if(!s){
   if(Date.now()>Date.parse('2026-09-14T04:00:00Z'))return;
   s={state:'RUNNING',started_ms:Date.now(),deadline_ms:Date.now()+600000,rows:[],retries:0,max_calls:5};
  }
  existing=s.rows.find(r=>r.input_sha256===hash);
  if(existing||s.state!=='RUNNING'||Date.now()>=s.deadline_ms||s.rows.length>=5||s.rows.some(r=>r.state==='RESERVED'))return;
  const [provider,model]=PDSA_LANES[s.rows.length];
  row={slot:s.rows.length,provider,model,input_sha256:hash,state:'RESERVED',reserved_utc:new Date().toISOString()};
  s.rows.push(row);await cell.ctx.storage.put(PDSA_KEY,s);acquired=true;
 });
 if(!acquired)return existing?.response??{error:{message:existing?.state??'BUDGET_OR_PENDING_HOLD'}};
 async function save(){await cell.ctx.blockConcurrencyWhile(async()=>{const current=await cell.ctx.storage.get(PDSA_KEY);if(current?.stop_requested){s.stop_requested=true;s.state='STOPPED_BY_EVALUATOR';}await cell.ctx.storage.put(PDSA_KEY,s);await env.CELL_STATE.put(PDSA_KEY+'.json',JSON.stringify(s));});}
 try{
  await save();
  if(row.provider==='kimi'){
   const q=await refreshQuota(cell,env);
   if(!quotaFresh(q)||!q.rows?.length||q.rows.some(x=>!x.consistent||x.remaining/x.limit<0.20))throw Error('QUOTA_HOLD');
  }
  if(row.provider==='openrouter'){
   const r=await fetch('https://openrouter.ai/api/v1/models',{signal:AbortSignal.timeout(15000)});
   if(!r.ok)throw Error('CATALOG_HOLD');
   const m=(await r.json()).data?.find(x=>x.id===row.model);
   if(!m||Number(m.pricing?.prompt)!==0||Number(m.pricing?.completion)!==0)throw Error('PRICE_HOLD');
  }
  if(Date.now()+95000>s.deadline_ms)throw Error('DEADLINE_HOLD');
  row.dispatched=true;await save(); // Reservation survives transport ambiguity.
  const google=row.provider==='google-ai-studio';
  const query=google?{contents:[{role:'user',parts:[{text:input.messages.map(m=>m.role+': '+m.content).join('\n\n')}]}],generationConfig:{maxOutputTokens:8192,candidateCount:1}}:
   {model:row.model,messages:input.messages,max_tokens:8192,temperature:1,stream:false,...(row.provider==='openrouter'?{provider:{max_price:{prompt:0,completion:0},allow_fallbacks:false}}:{})};
  let timer;
  const {r,b}=await Promise.race([(async()=>{
   const r=row.provider==='kimi'?await fetch('https://api.kimi.ai/coding/v1/chat/completions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${env.KIMI_API_KEY}`},body:JSON.stringify(query),redirect:'manual',signal:AbortSignal.timeout(90000)}):
    await env.AI.gateway('hfo-gen-140-cloudflare').run({provider:row.provider,endpoint:google?`v1beta/models/${row.model}:generateContent`:'chat/completions',headers:{'cf-aig-byok-alias':'default','cf-aig-skip-cache':'true','cf-aig-max-attempts':'1','cf-aig-request-timeout':'90000'},config:{maxAttempts:1,requestTimeout:90000},query});
   return {r,b:await dailyJson(r)};
  })(),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('AMBIGUOUS_TIMEOUT')),95000);})]).finally(()=>clearTimeout(timer));
  row.http_status=r.status;row.model_returned=google?b.modelVersion:b.model;
  row.usage=google?b.usageMetadata:b.usage;
  if(!r.ok||row.model_returned!==row.model)throw Error('PROVIDER_OR_IDENTITY_HOLD');
  const content=google?(b.candidates?.[0]?.content?.parts??[]).filter(x=>!x.thought).map(x=>x.text??'').join(''):b.choices?.[0]?.message?.content;
  if(typeof content!=='string'||!content.trim()||content.length>24000)throw Error('CONTENT_HOLD');
  row.response={id:PDSA_KEY+'-'+row.slot,object:'chat.completion',created:Math.floor(Date.now()/1000),model:row.model,choices:[{index:0,finish_reason:'stop',message:{role:'assistant',content}}],usage:google?{prompt_tokens:b.usageMetadata?.promptTokenCount??0,completion_tokens:b.usageMetadata?.candidatesTokenCount??0,total_tokens:b.usageMetadata?.totalTokenCount??0}:b.usage};
  row.state='RETURNED';row.finished_utc=new Date().toISOString();
  if(s.rows.length===5)s.state='CALL_BUDGET_EXHAUSTED';await save();return row.response;
 }catch(e){
  row.state=e.message==='AMBIGUOUS_TIMEOUT'?'AMBIGUOUS_NO_RETRY':'HOLD_NO_RETRY';
  row.reason=e.message;row.response={error:{message:row.state}};s.state='STOPPED';await save();return row.response;
 }
}
