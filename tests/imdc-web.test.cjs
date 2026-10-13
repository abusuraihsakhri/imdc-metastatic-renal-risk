const test=require('node:test');
const assert=require('node:assert/strict');
const {factors,calculate,parseCSV,makeCSV}=require('../web/imdc.js');
const flags=n=>Object.fromEntries(factors.map(([key],i)=>[key,i<n?'yes':'no']));
for(const [n,group] of [[0,'Favorable'],[1,'Intermediate'],[2,'Intermediate'],[3,'Poor'],[6,'Poor']]) {
 test('IMDC grouping at '+n,()=>{
  const result=calculate(flags(n));
  assert.equal(result.score,n);
  assert.equal(result.classification,group);
 });
}
test('all 64 factor permutations',()=>{
 for(let bits=0;bits<64;bits++){
  const data=Object.fromEntries(factors.map(([key],i)=>[key,Boolean(bits&(1<<i))]));
  assert.equal(calculate(data).score,Object.values(data).filter(Boolean).length);
 }
});
test('reject missing unknown and ambiguous factor values',()=>{
 assert.throws(()=>calculate({}));
 assert.throws(()=>calculate({...flags(0),unknown:true}));
 assert.throws(()=>calculate({...flags(0),kps_below_80:'maybe'}));
});
test('quoted comma CRLF and malformed CSV',()=>{
 assert.deepEqual(parseCSV('case_id,x\r\n"A, ""B""",yes\r\n'),[['case_id','x'],['A, "B"','yes']]);
 assert.throws(()=>parseCSV('"unclosed'));
 assert.throws(()=>parseCSV('"closed"trailing'));
});
test('prevent exported formula cells',()=>{
 assert.ok(makeCSV([['case_id'],['=HYPERLINK(1)']]).includes("'=HYPERLINK"));
});
