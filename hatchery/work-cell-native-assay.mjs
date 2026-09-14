// Real local DO/R2 restart. NativeJob service and all model egress are fixtures.
import {createRequire} from 'node:module';
import {readFileSync,mkdirSync,mkdtempSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {Miniflare,convertV4MiniflareOptions}=require(process.env.MINIFLARE_MODULE??'miniflare');
const source=['pdsa-budget.mjs','work-cell.mjs'].map(n=>readFileSync(new URL(n,import.meta.url),'utf8')).join('\n');
const parent=readFileSync(new URL('packing-fixture/parent.pck',import.meta.url),'utf8');
const hash=x=>createHash('sha256').update(x).digest('hex');
const canonical=x=>Array.isArray(x)?'['+x.map(canonical).join(',')+']':x&&typeof x==='object'?'{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')+'}':JSON.stringify(x);
const script=`import {DurableObject} from 'cloudflare:workers';
const Date=class extends globalThis.Date{static now(){return globalThis.Date.parse('2026-09-14T05:30:00Z')}};
async function vpsHash(s){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s))),b=>b.toString(16).padStart(2,'0')).join('')}
async function refreshQuota(){return {rows:[{consistent:true,remaining:100,limit:100}]}};function quotaFresh(){return true};async function dailyJson(r){return r.json()};
${source}
export class Cell extends DurableObject{
 async run(action,input){
  const env={CELL_STATE:this.env.CELL_STATE,AI:{gateway:()=>({run:()=>fetch('https://fixture.invalid/google')})},NATIVE_JOBS:{start:async r=>{await this.ctx.storage.put('fixture:native','running');return {job_id:r.job_id,workflow_id:r.job_id}},status:async()=>({status:await this.ctx.storage.get('fixture:native')}),submit:async()=>{await this.ctx.storage.put('fixture:native','complete')}}};
  return workCell(this,env,action,input);
 }
}
export default {async fetch(request,env){const {action,input}=await request.json();try{return Response.json(await env.CELL.get(env.CELL.idFromName('assay')).run(action,input))}catch(e){return Response.json({error:e.message},{status:400})}}};`;
mkdirSync('.wrangler',{recursive:true});const dir=mkdtempSync(resolve('.wrangler/work-cell-'));
let calls=0,mf;
const options={modules:true,script,compatibilityDate:'2026-09-02',durableObjects:{CELL:'Cell'},r2Buckets:['CELL_STATE'],resourcePersistencePath:dir+'/shared',isolatedResourcePersistencePath:dir+'/isolated',outboundService:async r=>{
 const h=new URL(r.url).hostname;assert.ok(['api.kimi.ai','fixture.invalid'].includes(h));calls++;
 return Response.json(h==='api.kimi.ai'?{model:'k3-256k',choices:[{message:{content:'fixture'}}]}:{modelVersion:'gemini-3.5-flash-lite',candidates:[{content:{parts:[{text:'fixture'}]}}]});
}};
const boot=()=>new Miniflare(convertV4MiniflareOptions?convertV4MiniflareOptions(options):options);
const run=async(action,input)=>(await mf.dispatchFetch('http://local/',{method:'POST',body:JSON.stringify({action,input})})).json();
const context={parent_sha256:hash(parent),evaluator_sha256:'a'.repeat(64)};
const manifest={abi:'gen142.hatchery/0',work_id:'gen142-work-cell-20260914-r1',profile:'packing.recipe.v1',context,context_sha256:hash(canonical(context)),limits:{provider_requests:2,max_usd:0,lifetime_seconds:600,generations:2}};
const model=n=>({model:'packing-cell',messages:[{role:'system',content:'Immutable context'},{role:'user',content:'Delta '+n}]});
const generation=n=>({generation:n,program_sha256:hash('recipe '+n),content:parent,metrics:{reason:'COMPLETE',trial_count:8}});
try{
 mf=boot();assert.equal((await run('admit',manifest)).state,'RUNNING');await run('model',model(1));assert.equal((await run('generation',generation(1))).accepted,true);
 await mf.dispose();mf=boot();const restored=await run('status');assert.equal(restored.generations.length,1);assert.equal(restored.model_context_sha256,hash(canonical(model(1).messages[0])));
 await run('model',model(1));assert.equal(calls,1);
 const second=await run('model',model(2));assert.ok(!second.error,JSON.stringify(second));assert.equal((await run('generation',generation(2))).accepted,true);
 const done=await run('finish');assert.equal(done.native.status,'complete');assert.equal(done.generations.length,2);assert.equal(done.context_use_count,2);assert.equal(calls,2);
 const stopped=await run('model',model(3));assert.ok(stopped.error);assert.equal(calls,2);
 console.log(JSON.stringify({status:'PASS',runtime:'local-workerd',compatibility_date:'2026-09-02',restored_generations:1,verified_generations:2,fixture_model_calls:calls,live_model_calls:0,context_reuses:1,claim_ceiling:'Native local DO and R2 persistence across runtime replacement; mocked Workflow service and model egress, not hosted acceptance.'}));
}finally{if(mf)await mf.dispose()}
