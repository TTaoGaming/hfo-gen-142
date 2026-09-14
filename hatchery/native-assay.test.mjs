import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import test from 'node:test';
const code=readFileSync(new URL('native-assay.mjs',import.meta.url),'utf8');
const fixture='{"items":[{"count":1,"text":"applications"},{"count":1,"text":"evolution"},{"count":2,"text":"research"}],"total":4}';
function setup(fail=false){
 const store=new Map();let starts=0,submits=0,lock=Promise.resolve();
 class FixtureDate extends Date { constructor(...args){super(...(args.length?args:['2026-09-14T01:00:00Z']));} static now(){return Date.parse('2026-09-14T01:00:00Z');} }
 const api=vm.runInNewContext(code+';hatcheryNativeAssay',{Date:FixtureDate,JSON,vpsCanonical:JSON.stringify,vpsHash:async x=>createHash('sha256').update(x).digest('hex')});
 const cell={ctx:{storage:{get:async k=>store.get(k),put:async(k,v)=>store.set(k,structuredClone(v))},blockConcurrencyWhile:fn=>{const next=lock.then(fn);lock=next.catch(()=>{});return next;}}};
 const env={CELL_STATE:{put:async()=>{}},NATIVE_JOBS:{start:async()=>{starts++;return {workflow_id:'fixture'};},status:async()=>({status:'complete'}),submit:async()=>{submits++;if(fail)throw Error('unknown');}}};
 return {call:(a,t)=>api(cell,env,a,t),counts:()=>({starts,submits})};
}
test('replacement, duplicate and conflicting payload',async()=>{
 const x=setup();await x.call('start');assert.equal((await x.call('start')).state,'EXISTS_NO_RESTART');
 assert.equal((await x.call('submit','wrong')).state,'CONFLICT_REJECTED');
 await Promise.all([x.call('submit',fixture),x.call('submit',fixture)]);
 assert.deepEqual(x.counts(),{starts:1,submits:1});
 assert.equal((await x.call('status')).receipt.accepted_effect_count,1);
});
test('ambiguous event send is retained without replay',async()=>{
 const x=setup(true);await x.call('start');await assert.rejects(x.call('submit',fixture));
 assert.equal((await x.call('submit',fixture)).state,'EFFECT_RESERVED');
 assert.deepEqual(x.counts(),{starts:1,submits:1});
});
