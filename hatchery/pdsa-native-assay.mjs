// Native workerd assay. All outgoing requests terminate in the fixture callback.
import {createRequire} from 'node:module';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {Miniflare,convertV4MiniflareOptions}=require(process.env.MINIFLARE_MODULE ?? 'miniflare');
const source=readFileSync(new URL('pdsa-budget.mjs',import.meta.url),'utf8');
const script=`import { DurableObject } from 'cloudflare:workers';
const Date=class extends globalThis.Date {static now(){return globalThis.Date.parse('2026-09-14T02:00:00Z')}};
async function vpsHash(s){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s))),b=>b.toString(16).padStart(2,'0')).join('')}
async function refreshQuota(){return (await fetch('https://fixture.invalid/quota')).json()}
function quotaFresh(){return true}
async function dailyJson(r){return r.json()}
${source}
export class Cell extends DurableObject {async run(input){return pdsaBudget(this,this.env,input)}}
export default {async fetch(request,env){const url=new URL(request.url);const stub=env.CELL.get(env.CELL.idFromName(url.pathname));return Response.json(await stub.run(await request.json()))}};
`;
let mode='quota',calls=0,releaseQuota,quotaEntered,releaseCall,callEntered;
const quotaGate=new Promise(r=>releaseQuota=r),quotaStarted=new Promise(r=>quotaEntered=r);
const callGate=new Promise(r=>releaseCall=r),callStarted=new Promise(r=>callEntered=r);
const compatibilityDate=process.env.ASSAY_COMPATIBILITY_DATE??'2026-09-02';
const options={modules:true,script,compatibilityDate,durableObjects:{CELL:'Cell'},r2Buckets:['CELL_STATE'],outboundService:async request=>{
 const url=new URL(request.url);
 if(url.hostname==='fixture.invalid'){
  if(mode==='quota'){quotaEntered();await quotaGate;}
  return Response.json({rows:[{consistent:true,remaining:100,limit:100}]});
 }
 assert.equal(url.hostname,'api.kimi.ai');calls++;
 if(mode==='inflight'){callEntered();await callGate;}
 return Response.json({model:'k3-256k',choices:[{message:{content:'{}'}}]});
}};
const mf=new Miniflare(convertV4MiniflareOptions ? convertV4MiniflareOptions(options) : options);
const run=async(name,input)=>(await mf.dispatchFetch('http://local/'+name,{method:'POST',body:JSON.stringify(input)})).json();
const request={model:'packing-cell',messages:[{role:'user',content:'fixture'}]};
try{
 const first=run('before',request);await quotaStarted;
 assert.equal((await run('before','stop')).stopped,true);assert.equal(calls,0);
 releaseQuota();await first;assert.equal(calls,0);
 await run('before',request);assert.equal(calls,0);
 assert.equal((await run('before',null)).state,'STOPPED_BY_EVALUATOR');
 mode='inflight';const second=run('during',request);await callStarted;
 assert.equal((await run('during','stop')).stopped,true);assert.equal(calls,1);
 releaseCall();await second;
 assert.equal((await run('during',null)).state,'STOPPED_BY_EVALUATOR');
 await run('during',{...request,messages:[{role:'user',content:'next'}]});assert.equal(calls,1);
 console.log(JSON.stringify({status:'PASS',runtime:'Miniflare/workerd',compatibilityDate,source_sha256_lf:createHash('sha256').update(source.replaceAll('\r\n','\n')).digest('hex'),quota_wait_stop_dispatches:0,inflight_stop_total_dispatches:1,live_provider_calls:0,claim_ceiling:'Native local DO and R2 gates; mocked egress and older installed compatibility date, not hosted deployment or eviction recovery'}));
}finally{releaseQuota();releaseCall();await mf.dispose()}
