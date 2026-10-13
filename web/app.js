'use strict';
const {factors,calculate,parseCSV,makeCSV}=window.IMDC;
const form=document.getElementById('risk-form');
const singleMessage=document.getElementById('single-message');
const resultBox=document.getElementById('single-result');
const fileInput=document.getElementById('batch-file');
const batchMessage=document.getElementById('batch-message');
const saveButton=document.getElementById('save-csv');
let csvData=null;
function status(element,value,invalid) {
 element.textContent=value;
 element.className=invalid?'feedback error':'feedback';
}
for(const [name,labelText] of factors) {
 const line=document.createElement('div');line.className='criterion';
 const label=document.createElement('label');label.htmlFor=name;label.textContent=labelText;
 const select=document.createElement('select');select.name=name;select.id=name;select.required=true;
 [['','Choose…'],['yes','Yes'],['no','No']].forEach(pair=>{
  const option=document.createElement('option');option.value=pair[0];option.textContent=pair[1];select.append(option);
 });
 line.append(label,select);document.getElementById('factor-fields').append(line);
}
form.addEventListener('submit',event=>{
 event.preventDefault();
 try {
  const input=Object.fromEntries(factors.map(([key])=>[key,form.elements[key].value]));
  const result=calculate(input);
  const title=document.createElement('strong');
  title.textContent=result.score+' / 6 — '+result.classification+' risk';
  const detail=document.createElement('p');
  detail.textContent=result.risk_factors.length?'Adverse factors: '+result.risk_factors.join('; '):'No adverse factors present.';
  resultBox.replaceChildren(title,detail);resultBox.hidden=false;
  status(singleMessage,'Calculated entirely on your device.',false);
 } catch(err) {resultBox.hidden=true;status(singleMessage,err.message,true);}
});
form.addEventListener('reset',()=>{
 resultBox.hidden=true;status(singleMessage,'Assess all six factors before calculating.',false);
});
function download(text,filename) {
 const blob=new Blob([text],{type:'text/csv;charset=utf-8'});
 const url=URL.createObjectURL(blob);
 const link=document.createElement('a');
 link.href=url;link.download=filename;document.body.append(link);link.click();link.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
}
document.getElementById('get-template').addEventListener('click',()=>{
 download(makeCSV([['case_id',...factors.map(f=>f[0])],['CASE-001',...factors.map(()=>'no')]]),'imdc-template.csv');
});
function preview(rows) {
 const element=document.getElementById('preview');element.replaceChildren();
 const table=document.createElement('table');
 const caption=document.createElement('caption');caption.textContent='First 10 scored cases';table.append(caption);
 const header=document.createElement('tr');
 ['Case','Score','Risk group'].forEach(x=>{const th=document.createElement('th');th.textContent=x;header.append(th);});
 const thead=document.createElement('thead');thead.append(header);table.append(thead);
 const tbody=document.createElement('tbody');
 rows.slice(0,10).forEach((r,i)=>{
  const tr=document.createElement('tr');
  [r.case_id||String(i+1),r.score,r.classification].forEach(x=>{
   const td=document.createElement('td');td.textContent=String(x);tr.append(td);
  });
  tbody.append(tr);
 });
 table.append(tbody);element.append(table);
}
fileInput.addEventListener('change',async()=>{
 csvData=null;saveButton.disabled=true;document.getElementById('preview').replaceChildren();
 const file=fileInput.files[0];if(!file)return;
 if(file.size>2*1024*1024){status(batchMessage,'CSV exceeds 2 MB limit',true);return;}
 try {
  const table=parseCSV(await file.text());
  if(!table.length)throw new Error('Empty CSV');
  const headers=table[0].map(x=>x.trim());
  const allowed=['case_id',...factors.map(x=>x[0])];
  if(new Set(headers).size!==headers.length)throw new Error('Duplicate column names');
  if(headers.some(x=>!allowed.includes(x)))throw new Error('Unknown CSV column');
  if(factors.some(([key])=>!headers.includes(key)))throw new Error('CSV requires all six IMDC columns');
  if(table.length>10001)throw new Error('Maximum 10,000 cases per file');
  const scored=[];
  for(let i=1;i<table.length;i++){
   if(table[i].length!==headers.length)throw new Error('Row '+(i+1)+': column count mismatch');
   const row=Object.fromEntries(headers.map((h,j)=>[h,table[i][j]]));
   let risk;
   try {risk=calculate(Object.fromEntries(factors.map(([k])=>[k,row[k]])));}
   catch(err){throw new Error('Row '+(i+1)+': '+err.message);}
   scored.push({...row,score:risk.score,classification:risk.classification});
  }
  if(!scored.length)throw new Error('CSV has no cases');
  csvData=makeCSV([headers.concat(['score','classification']),...scored.map(r=>headers.map(h=>r[h]).concat([r.score,r.classification]))]);
  preview(scored);saveButton.disabled=false;
  status(batchMessage,'Scored '+scored.length+' cases locally. No upload occurred.',false);
 } catch(err){status(batchMessage,err.message,true);}
});
saveButton.addEventListener('click',()=>{if(csvData)download(csvData,'imdc-results.csv');});
