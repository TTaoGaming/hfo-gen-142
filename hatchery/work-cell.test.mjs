import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const source=['pdsa-budget.mjs','work-cell.mjs'].map(n=>readFileSync(new URL(n,import.meta.url),'utf8')).join('\n');
const hash=x=>createHash('sha256').update(x).digest('hex');
const parent=readFileSync(new URL('packing-fixture/parent.pck',import.meta.url),'utf8');
function setup(){
 const data=new Map(),objects=new Map();let lock=Promise.resolve(),calls=0,starts=0,submits=0,nativeStatus='running';
 class Now extends Date{static now(){return Date.parse('2026-09-14T05:30:00Z');}}
 const context={Date:Now,TextEncoder,AbortSignal,setTimeout,clearTimeout,JSON,vpsHash:async x=>hash(x),dailyJson:async r=>r.json(),quotaFresh:()=>true,refreshQuota:async()=>({rows:[{consistent:true,remaining:100,limit:100}]}),fetch:async()=>{calls++;return {ok:true,status:200,json:async()=>({model:'k3-256k',choices:[{message:{content:'fixture recipe'}}]})};}};
 const f=vm.runInNewContext(source+';({workCell,workCanonical,workVerifyPacking})',context);
 const cell={ctx:{storage:{get:async k=>structuredClone(data.get(k)),put:async(k,v)=>data.set(k,structuredClone(v))},blockConcurrencyWhile:fn=>{const p=lock.then(fn);lock=p.catch(()=>{});return p;}}};
 const env={CELL_STATE:{put:async(k,v)=>objects.set(k,v)},NATIVE_JOBS:{start:async r=>{starts++;return {job_id:r.job_id,workflow_id:r.job_id};},status:async()=>({status:nativeStatus}),submit:async()=>{submits++;nativeStatus='complete';}},AI:{gateway:()=>({run:async()=>{calls++;return {ok:true,status:200,json:async()=>({modelVersion:'gemini-3.5-flash-lite',candidates:[{content:{parts:[{text:'fixture recipe 2'}]}}]})};}})}};
 const ctx={parent_sha256:hash(parent),evaluator_sha256:'a'.repeat(64),instructions:'Pinned packing task'};
 const manifest={abi:'gen142.hatchery/0',work_id:'gen142-work-cell-20260914-r1',profile:'packing.recipe.v1',context:ctx,context_sha256:hash(f.workCanonical(ctx)),limits:{provider_requests:2,max_usd:0,lifetime_seconds:600,generations:2}};
 return {run:(action,input,workId)=>f.workCell(cell,env,action,input,workId),canonical:f.workCanonical,manifest,objects,data,verify:f.workVerifyPacking,counters:()=>({calls,starts,submits}),replace:()=>({ctx:cell.ctx})};
}
const model=n=>({model:'packing-cell',messages:[{role:'system',content:'Immutable task instructions'},{role:'user',content:'Delta '+n}]});
const generation=n=>({generation:n,program_sha256:hash('recipe '+n),content:parent,metrics:{reason:'COMPLETE',trial_count:8,radius:0.309963933216626}});
test('no admission or unsupported workload creates no provider effect',async()=>{
 const x=setup();await assert.rejects(x.run('model',model(1)),/MISSION_NOT_RUNNING/);
 await assert.rejects(x.run('admit',{...x.manifest,profile:'image.generate.v1'}),/WORKLOAD_PROFILE/);
 await assert.rejects(x.run('admit',{...x.manifest,limits:{...x.manifest.limits,provider_requests:5}}),/CAP_BINDING/);
 assert.equal(x.counters().calls,0);assert.equal(x.counters().starts,0);
});
test('admission and generations are idempotent and immutable',async()=>{
 const x=setup();await x.run('admit',x.manifest);await x.run('admit',x.manifest);assert.equal(x.counters().starts,1);
 await assert.rejects(x.run('admit',{...x.manifest,context_sha256:'0'.repeat(64)}),/CONTEXT_HASH/);
 await x.run('model',model(1));await x.run('model',model(1));assert.equal(x.counters().calls,1);
 await assert.rejects(x.run('model',model(2)),/PREVIOUS_RESULT_NOT_VERIFIED/);
 await x.run('generation',generation(1));assert.equal((await x.run('generation',generation(1))).replayed,true);
 await assert.rejects(x.run('generation',{...generation(1),program_sha256:'0'.repeat(64)}),/GENERATION_CONFLICT/);
 await assert.rejects(x.run('model',{...model(2),messages:[{role:'system',content:'changed'},model(2).messages[1]]}),/MODEL_CONTEXT_CHANGED/);
 await x.run('model',model(2));await x.run('generation',generation(2));await x.run('finish');await x.run('finish');
 const s=await x.run('status');assert.equal(s.generations.length,2);assert.equal(s.context_use_count,2);assert.equal(x.counters().calls,2);assert.equal(x.counters().submits,1);
 assert.equal(s.native.status,'complete');assert.equal(s.memory.last_verified_generation,2);
 await x.run('model',model(1));assert.equal(x.counters().calls,2);
});
test('integer verifier catches overlap, wall violations and wrong shape',()=>{
 const x=setup();assert.equal(x.verify(parent).pair_checks,7021);
 const lines=parent.trimEnd().split('\n');lines[3]=lines[2];assert.throws(()=>x.verify(lines.join('\n')),/OVERLAP/);
 lines[3]='2 0 0 0 0 0';assert.throws(()=>x.verify(lines.join('\n')),/CONTAINMENT/);
 assert.throws(()=>x.verify(parent+'0 0 0 0 0 0\n'),/PACKING_SHAPE/);
});
test('stop prevents new model work and incomplete finish is refused',async()=>{
 const x=setup();await x.run('admit',x.manifest);await assert.rejects(x.run('finish'),/TWO_VERIFIED_GENERATIONS_REQUIRED/);
 await x.run('stop');await assert.rejects(x.run('model',model(1)),/MISSION_NOT_RUNNING/);assert.equal(x.counters().calls,0);
});
test('admitted input jobs evaluate two distinct inputs without any provider effect',async()=>{
 const x=setup(),id='gen142-work-cell-input-20260914-r1';
 const context={...x.manifest.context,proposals:['recipe A','recipe B']};
 const manifest={...x.manifest,work_id:id,proposal_source:'admitted-input',limits:{...x.manifest.limits,provider_requests:0},context,context_sha256:hash(x.canonical(context))};
 const run=(action,input)=>x.run(action,input,id);
 await run('admit',manifest);
 assert.equal((await run('model',model(1))).choices[0].message.content,'recipe A');
 await run('model',model(1));await run('generation',generation(1));
 assert.equal((await run('model',model(2))).choices[0].message.content,'recipe B');
 await run('generation',generation(2));const final=await run('finish');
 assert.equal(final.generations.length,2);assert.equal(final.input_rows.length,2);assert.equal(final.budget.rows.length,0);assert.equal(final.native.status,'complete');assert.equal(x.counters().calls,0);
 await assert.rejects(run('admit',{...manifest,limits:{...manifest.limits,provider_requests:1}}),/CAP_BINDING/);
});
test('failed work closes native workflow without pretending a verified generation',async()=>{
 const x=setup();await x.run('admit',x.manifest);
 const final=await x.run('fail',{reason:'PROVIDER_HOLD'});
 assert.equal(final.result.verdict,'reject');assert.equal(final.generations.length,0);assert.equal(final.native.status,'complete');
 await x.run('fail',{reason:'PROVIDER_HOLD'});assert.equal(x.counters().submits,1);assert.equal(x.counters().calls,0);
 await assert.rejects(x.run('model',model(1)),/MISSION_NOT_RUNNING/);
});
