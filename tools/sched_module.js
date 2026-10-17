(function(){
days.push(
 {kitchen:620,out:null,nightBath:2,nightKit:1,living:[[540,600]],ev:[[420,'bed'],[600,'living'],[620,'kitchen'],[140,'bath'],[250,'bath']]},
 {kitchen:455,out:540,nightBath:7,nightKit:4,living:[[560,640]],ev:[[400,'bed'],[455,'kitchen'],[540,'out'],[40,'bath'],[100,'bath'],[150,'bath'],[210,'bath'],[260,'bath'],[300,'bath'],[330,'bath']]},
 {kitchen:410,out:480,nightBath:1,nightKit:0,living:[[560,640]],ev:[[360,'bed'],[410,'kitchen'],[480,'out'],[200,'bath']]});
const sb=document.getElementById('b0').parentNode;
['Late riser','Night wanderer','Early bird'].forEach((n,i)=>{const b=document.createElement('button');b.textContent=n;b.onclick=()=>setDay(i+2);sb.appendChild(b)});
const sn=document.createElement('div');sn.className='sm';sn.id='scnNote';sn.style.marginTop='8px';sb.parentNode.appendChild(sn);
let taken={},spoken={},simT=665;
setDay=function(i){day=i;sb.querySelectorAll('button').forEach((b,j)=>b.className=j==i?'on':'');taken={};spoken={};resetEsc()};
const S=[['Morning tablets',480,'\uD83D\uDC8A'],['Breakfast',510,'\uD83C\uDF7D\uFE0F'],['Lunch',780,'\uD83C\uDF7D\uFE0F'],['Evening tablets',1080,'\uD83D\uDC8A'],['Dinner',1230,'\uD83C\uDF7D\uFE0F']];
const say2=t=>{try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.rate=.92;speechSynthesis.speak(u)}catch(e){}};
const sp=t=>(window.say||say2)(t);
function stat(i){const t=S[i][1],d=days[day],med=i==0||i==3;
 if(med&&taken[i])return['done','taken'];
 if(!med&&d.kitchen!==null){if(i==1&&simT>=d.kitchen)return[d.kitchen>t+45?'late':'done','kitchen at '+fmt(d.kitchen)];if(i!=1&&simT>t+30)return['done','kitchen activity']}
 if(simT<t-30)return['up','due '+fmt(t)];
 if(simT<=t+60)return['due','due now'];
 return['miss','missed']}
function schedRender(){
 const el=document.getElementById('schedList'),al=document.getElementById('schedAlert');if(!el)return;
 document.getElementById('simLbl').textContent='Simulated time: '+fmt(simT);el.innerHTML='';al.innerHTML='';let msg='',cls='ins';
 S.forEach(([n,t,ic],i)=>{const[s,tx]=stat(i),med=i==0||i==3,r=document.createElement('div');
  r.style.cssText='display:flex;gap:10px;align-items:center;padding:8px 0;border-top:1px solid var(--line)';
  const c={done:'var(--ok)',late:'var(--warn)',due:'var(--warn)',miss:'var(--bad)',up:'var(--mut)'}[s];
  r.innerHTML='<span>'+ic+'</span><div style="flex:1">'+n+'<div class="sm">'+fmt(t)+'</div></div><span class="sm" style="color:'+c+'">'+tx+'</span>';
  if(med&&(s=='due'||s=='miss')){const b=document.createElement('button');b.textContent='Mark taken';b.onclick=()=>{taken[i]=1;schedRender()};r.appendChild(b)}
  el.appendChild(r);
  if(med&&s=='due'){msg='Time for your '+n.toLowerCase()+', Mom.';if(!spoken[i]){spoken[i]=1;sp(msg)}}
  if(med&&s=='miss'){msg='Mom missed her '+n.toLowerCase()+'. Priya has been notified.';if(!spoken['m'+i]){spoken['m'+i]=1;sp(msg)}}
  if(!med&&s=='miss'&&!msg)msg=n+' not detected. Gentle check-in suggested.'});
 if(msg){al.className=cls;al.textContent='\uD83D\uDD14 '+msg;al.style.margin='8px 0'}else al.className=''}
function note(){const d=days[day];sn.textContent='Kitchen: '+(d.kitchen==null?'no visit yet':fmt(d.kitchen))+' | Outing: '+(d.out==null?'none yet':fmt(d.out))+' | Overnight bathroom trips: '+d.nightBath+' | Late-night kitchen visits: '+d.nightKit}
document.getElementById('simSl').oninput=e=>{simT=+e.target.value;schedRender()};
const _r2=render;render=function(){_r2();note();schedRender()};
render();
})();
