import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const source=readFileSync(new URL('pdsa-budget.mjs',import.meta.url),'utf8');
function setup(fail=false,defer=false,quotaHook=null,persistHook=null){
 const data=new Map();let lock=Promise.resolve(),calls=0;
 let release,entered;const gate=new Promise(r=>release=r),started=new Promise(r=>entered=r);
 const response=model=>({ok:true,status:200,json:async()=>({model,modelVersion:model,choices:[{message:{content:'{}'}}],candidates:[{content:{parts:[{text:'{}'}]}}]})});
 const dispatch=async(model)=>{calls++;entered();if(defer)await gate;if(fail)throw Error('UNKNOWN');return response(model);};
 class Now extends Date{constructor(...x){super(...(x.length?x:['2026-09-14T02:00:00Z']));} static now(){return Date.parse('2026-09-14T02:00:00Z');}}
 const context={Date:Now,AbortSignal,setTimeout,clearTimeout,JSON,fetch:async(url,opts)=>url.includes('/models')?{ok:true,json:async()=>({data:[{id:'nvidia/nemotron-3.5-lightning:free',pricing:{prompt:'0',completion:'0'}}]})}:dispatch(JSON.parse(opts.body).model),dailyJson:async r=>r.json(),vpsHash:async s=>createHash('sha256').update(s).digest('hex'),refreshQuota:async()=>{if(quotaHook)await quotaHook();return {rows:[{consistent:true,remaining:100,limit:100}]};},quotaFresh:()=>true};
 const fn=vm.runInNewContext(source+';pdsaBudget',context);
 const cell={ctx:{storage:{get:async k=>structuredClone(data.get(k)),put:async(k,v)=>data.set(k,structuredClone(v))},blockConcurrencyWhile:f=>{const x=lock.then(f);lock=x.catch(()=>{});return x;}}};
 const env={CELL_STATE:{put:async(k,v)=>{if(persistHook)await persistHook(JSON.parse(v));}},AI:{gateway:()=>({run:async q=>dispatch(q.query.model??q.endpoint.split('/')[2].split(':')[0])})}};
 return {run:q=>fn(cell,env,q),calls:()=>calls,release,started};
}
const request=n=>({model:'packing-cell',messages:[{role:'user',content:'recipe '+n}]});
test('five slots, replay, concurrency and stop',async()=>{
 const x=setup();await Promise.all([x.run(request(0)),x.run(request(0))]);assert.equal(x.calls(),1);
 await x.run(request(0));assert.equal(x.calls(),1);
 for(let i=1;i<5;i++)await x.run(request(i));
 assert.equal(x.calls(),5);await x.run(request(5));assert.equal(x.calls(),5);
 const s=await x.run(null);assert.equal(s.rows.filter(r=>r.provider==='kimi').length,2);
 const y=setup();await y.run(request(0));await y.run('stop');await y.run(request(1));assert.equal(y.calls(),1);
});
test('uncertain provider completion stops all dispatch',async()=>{
 const x=setup(true);await x.run(request(0));await x.run(request(0));await x.run(request(1));assert.equal(x.calls(),1);
 assert.equal((await x.run(null)).state,'STOPPED');
});
test('stop during an in-flight call survives its late completion',async()=>{
 const x=setup(false,true),pending=x.run(request(0));await x.started;
 assert.equal((await x.run('stop')).stopped,true);
 await x.run(request(1));assert.equal(x.calls(),1);
 x.release();await pending;
 assert.equal((await x.run(null)).state,'STOPPED_BY_EVALUATOR');
 await x.run(request(2));assert.equal(x.calls(),1);
});

// Mandatory regression from the N2 incident. All transport is mocked.
test('B1: stop during quota check prevents dispatch',async()=>{
 let entered,release;
 const checking=new Promise(r=>entered=r),gate=new Promise(r=>release=r);
 const x=setup(false,false,async()=>{entered();await gate;});
 const pending=x.run(request(0));await checking;
 const stopped=await x.run('stop');const callsAtStop=x.calls();
 release();await pending;
 const state=await x.run(null);
 console.log(JSON.stringify({assay:'B1_STOP_DURING_QUOTA',source_sha256:createHash('sha256').update(source.replaceAll('\r\n','\n')).digest('hex'),stop_ack:stopped.stopped,calls_at_stop:callsAtStop,calls_after_release:x.calls(),final_state:state.state,live_provider_calls:0}));
 assert.equal(stopped.stopped,true);
 assert.equal(callsAtStop,0);
 assert.equal(x.calls(),0,'Stop was acknowledged before a provider call was dispatched');
 assert.equal(state.rows[0].dispatched,undefined);
 assert.equal(state.rows[0].reason,'STOP_BEFORE_DISPATCH');
 await x.run(request(0));await x.run(request(1));assert.equal(x.calls(),0);
});

test('stop queued during dispatch persistence acknowledges after send starts, before response',async()=>{
 let entered,release,once=false;
 const persisting=new Promise(r=>entered=r),gate=new Promise(r=>release=r);
 const x=setup(false,true,null,async s=>{
  if(s.rows[0]?.dispatched&&!once){once=true;entered();await gate;}
 });
 const pending=x.run(request(0));await persisting;
 let acknowledged=false;
 const stopping=x.run('stop').then(r=>{acknowledged=true;assert.equal(x.calls(),1);return r;});
 await Promise.resolve();assert.equal(acknowledged,false);assert.equal(x.calls(),0);
 release();await x.started;
 assert.equal((await stopping).stopped,true);
 x.release();await pending;
 assert.equal((await x.run(null)).state,'STOPPED_BY_EVALUATOR');
 await x.run(request(1));assert.equal(x.calls(),1);
});
