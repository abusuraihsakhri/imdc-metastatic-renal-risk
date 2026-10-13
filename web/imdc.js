/* IMDC/Heng risk calculator — six equally weighted adverse criteria. */
(function(root) {
'use strict';
const factors=Object.freeze([
 ['kps_below_80','Karnofsky performance status below 80%'],
 ['diagnosis_to_treatment_lt_1yr','Diagnosis to systemic treatment less than 1 year'],
 ['hemoglobin_below_lln','Hemoglobin below local lower limit of normal (LLN)'],
 ['corrected_calcium_above_uln','Corrected calcium above local upper limit of normal (ULN)'],
 ['neutrophils_above_uln','Neutrophils above local ULN'],
 ['platelets_above_uln','Platelets above local ULN']
]);
function parseFlag(value,name) {
 if(typeof value==='boolean') return value;
 if(value===0 || value===1) return Boolean(value);
 if(typeof value==='string') {
  const text=value.trim().toLowerCase();
  if(['yes','true','1'].includes(text)) return true;
  if(['no','false','0'].includes(text)) return false;
 }
 throw new Error(name+': use yes/no, true/false, or 1/0');
}
function calculate(data) {
 if(!data || typeof data!=='object' || Array.isArray(data)) throw new Error('All six IMDC factors are required');
 const keys=factors.map(f=>f[0]);
 if(Object.keys(data).some(k=>!keys.includes(k))) throw new Error('Unknown IMDC criterion');
 const flags={}, risk_factors=[];
 for(const [key,label] of factors) {
  if(!Object.prototype.hasOwnProperty.call(data,key)) throw new Error('Missing criterion '+key);
  flags[key]=parseFlag(data[key],key);
  if(flags[key]) risk_factors.push(label);
 }
 const score=risk_factors.length;
 return {score:score, classification:score===0?'Favorable':score<=2?'Intermediate':'Poor',risk_factors:risk_factors,factors:flags};
}
function parseCSV(text) {
 if(typeof text!=='string') throw new Error('CSV text is required');
 const s=text.replace(/^\uFEFF/,'');
 const rows=[]; let row=[],field='',quoted=false,closed=false;
 for(let i=0;i<s.length;i++) {
  const ch=s[i];
  if(quoted) {
   if(ch==='"') {
    if(s[i+1]==='"') {field+='"';i++;}
    else {quoted=false;closed=true;}
   } else field+=ch;
  } else if(ch===',') {
   row.push(field);field='';closed=false;
  } else if(ch==='\r' || ch==='\n') {
   if(ch==='\r' && s[i+1]==='\n') i++;
   row.push(field);
   if(row.some(x=>x!=='')) rows.push(row);
   row=[];field='';closed=false;
  } else if(ch==='"' && !field && !closed) quoted=true;
  else {
   if(closed || ch==='"') throw new Error('Malformed CSV quoting');
   field+=ch;
  }
 }
 if(quoted) throw new Error('Unclosed quoted CSV field');
 row.push(field);
 if(row.some(x=>x!=='')) rows.push(row);
 return rows;
}
function safeCell(value) {
 let s=String(value==null?'':value);
 if(/^[\t\r\n]/.test(s) || /^\s*[=+\-@]/.test(s)) s="'"+s;
 return '"'+s.replace(/"/g,'""')+'"';
}
function makeCSV(rows) {return rows.map(row=>row.map(safeCell).join(',')).join('\r\n')+'\r\n';}
const api={factors,calculate,parseCSV,makeCSV};
if(typeof module==='object' && module.exports) module.exports=api;
else root.IMDC=api;
})(typeof window!=='undefined'?window:globalThis);
