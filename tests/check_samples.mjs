import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
function load(file, control, initial){
 const html=fs.readFileSync(new URL('../samples/'+file,import.meta.url),'utf8');
 assert(!/<(?:script|img|iframe)[^>]+src\s*=|<link[^>]+href\s*=|\bfetch\s*\(|XMLHttpRequest|https?:\/\/[^<]*\.js/i.test(html),'external resource/request');
 const elements=new Map();
 function get(id){if(!elements.has(id))elements.set(id,{value:id===control?initial:'',textContent:'',dataset:{},attributes:{},addEventListener(){},setAttribute(k,v){this.attributes[k]=v}});return elements.get(id)}
 const document={querySelector:s=>get(s.slice(1)),getElementById:get,querySelectorAll:()=>[]};
 const context=vm.createContext({document,Math,Number,String});
 vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
 return {get,change:value=>{get(control).value=String(value);vm.runInContext('render()',context)}};
}
const boat=load('curiosity-buoyancy.html','cargo','300');
for(const [cargo,mass,draft,state] of [[0,200,'0.100 m','漂浮平衡'],[300,500,'0.250 m','漂浮平衡'],[790,990,'0.495 m','漂浮平衡'],[800,1000,'不适用','到达进水边界'],[1000,1200,'不适用','超过进水边界']]){
 boat.change(cargo);assert.equal(boat.get('mass').textContent,`${mass} kg`);assert.equal(boat.get('draft').textContent,draft);assert.equal(boat.get('state-title').textContent,state);
}
boat.change(800);const boundary=boat.get('hull').attributes.transform;boat.change(1000);assert.equal(boat.get('hull').attributes.transform,boundary,'out-of-model animation must stop at boundary');
const shadow=load('curiosity-shadow.html','angle','45');
for(const [angle,length] of [[5,'11.43 m'],[45,'1.00 m'],[85,'0.0875 m']]){shadow.change(angle);assert.equal(shadow.get('length').textContent,length);}
console.log('PASS: declared-model checkpoints, boundary stop, shadow endpoints; no external resources/request code. DOM stub checks do not replace browser operations.');
