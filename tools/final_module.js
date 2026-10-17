(function(){
const $=i=>document.getElementById(i),sp=t=>(window.say||(x=>{try{speechSynthesis.cancel();speechSynthesis.speak(new SpeechSynthesisUtterance(x))}catch(e){}}))(t);
const ls={get:k=>{try{return localStorage.getItem(k)}catch(e){return null}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}},del:k=>{try{localStorage.removeItem(k)}catch(e){}}};
const sty=document.createElement('style');sty.textContent='@keyframes grow2{from{transform:scaleY(0)}}';document.head.appendChild(sty);
let privOn=ls.get('cr_priv')=='1',role='priya',spokenB={},charged={},et=null;
const ROLES={priya:['Priya',null,'Sees everything and manages settings.'],mom:['Mom',null,'Sees exactly what the family sees, and controls privacy.'],
 sibling:['Sibling',['Routine compliance','Agent insight · vs 30-day baseline',"Today's activity",'Escalation · human first','Medicine and meal schedule','Weekly trend','Device batteries','Safety check · movement','Day ring','Water intake','Weather advice'],'Sees insights and alerts. No settings.'],
 neighbor:['Neighbor',['Escalation · human first','Emergency contacts'],'Sees emergency alerts only. No daily activity.'],
 doctor:['Doctor',['Weekly trend','Routine compliance','Agent insight · vs 30-day baseline','Water intake','Medicine and meal schedule'],'Sees trends and health summaries only.']};
const KEEP=['Privacy and consent',"Reverse check-in · Mom's view",'Emergency contacts','Escalation · human first','Weather advice'];
function applyView(){const al=ROLES[role][1];document.querySelectorAll('.card').forEach(c=>{const h=c.querySelector('h2'),t=h?h.textContent:'';let s=true;
 if(h){if(al&&!al.includes(t)&&t!=='Privacy and consent')s=false;if(privOn&&!KEEP.includes(t))s=false}else if(c.id==='privBanner')s=privOn;else if(privOn&&c.id!=='roleCard')s=false;
 c.style.display=s?'':'none'});$('roleNote').textContent=ROLES[role][2]}
function setPriv(v){privOn=v;ls.set('cr_priv',v?'1':'0');$('pauseBtn').textContent=v?'Resume monitoring':'Pause monitoring';$('privState').textContent=v?'Monitoring is paused. The family sees only the emergency button.':'Monitoring is on, with your consent.';applyView()}
function consentUI(){const c=ls.get('cr_consent');$('consentLine').textContent=c?'Consent given on '+new Date(+c).toLocaleDateString()+'. You can withdraw anytime.':'No consent recorded yet.'}
function showModal(){if($('consentModal'))return;const m=document.createElement('div');m.id='consentModal';m.style.cssText='position:fixed;inset:0;z-index:50;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;padding:16px';
 m.innerHTML='<div style="max-width:460px;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:14px;padding:18px"><h3 style="margin:0 0 8px">Hello Mom</h3><p>CareRing keeps a gentle eye on your daily routine so Priya knows you are well. It notes which room has motion and when. It never records video, audio or photos.</p><p>You choose who sees what. You can pause it at any time with one tap, and you can withdraw your consent whenever you like.</p><div class="row"><button class="p" id="cYes">I agree</button><button id="cNo">Not now</button></div></div>';
 document.body.appendChild(m);$('cYes').onclick=()=>{ls.set('cr_consent',Date.now());setPriv(false);consentUI();m.remove()};$('cNo').onclick=()=>{setPriv(true);m.remove()}}
$('pauseBtn').onclick=()=>setPriv(!privOn);$('withdrawBtn').onclick=()=>{ls.del('cr_consent');setPriv(true);consentUI();showModal()};
$('roleSel').onchange=e=>{role=e.target.value;applyView()};
const LV={0:[82,64,71],1:[78,14,66],2:[60,28,70],3:[75,52,12],4:[90,41,58]},DN=['Front Door doorbell','Kitchen camera','Bedroom camera'];
function batt(){const L=LV[day]||LV[0],el=$('battBody');el.innerHTML='';
 DN.forEach((n,i)=>{const k=day+'_'+i,v=charged[k]?100:L[i],c=v<=15?'var(--bad)':v<=30?'var(--warn)':'var(--ok)',r=document.createElement('div');r.style.cssText='display:flex;gap:10px;align-items:center;padding:6px 0';
  r.innerHTML='<div style="flex:1">'+n+'<div style="height:8px;border-radius:5px;background:var(--line);margin-top:4px;overflow:hidden"><div style="height:100%;width:'+v+'%;background:'+c+';transition:width .8s"></div></div></div><span class="sm" style="color:'+c+'">'+v+'%</span>';
  if(v<=30){const b=document.createElement('button');b.textContent='Mark charging';b.onclick=()=>{charged[k]=1;batt()};r.appendChild(b);if(v<=15&&!spokenB[k]){spokenB[k]=1;sp('Priya, the '+n.toLowerCase()+' battery is at '+v+' percent. Please charge it tonight.')}}
  el.appendChild(r)});
 $('battNote').textContent=L.some((v,i)=>v<=15&&!charged[day+'_'+i])?'A dead camera looks like no movement. Charge it tonight so a quiet camera is not mistaken for a quiet day.':'All devices have enough charge.'}
const WK={0:[88,91,87,90,89,92,90],1:[85,80,74,68,60,55,50],2:[88,86,90,84,85,83,86],3:[84,88,70,92,66,90,60],4:[92,95,91,94,93,96,94]};
function trend(){const w=WK[day]||WK[0],a=w.reduce((x,y)=>x+y,0)/7,ch=Math.round((a-90)/90*100);let h='';
 w.forEach((v,i)=>{h+='<rect x="'+(20+i*38)+'" y="'+(90-v*.8)+'" width="26" height="'+v*.8+'" rx="4" fill="'+(v<70?'var(--warn)':'var(--acc)')+'" style="transform-box:fill-box;transform-origin:bottom;animation:grow2 .7s both;animation-delay:'+i*.08+'s"/><text x="'+(33+i*38)+'" y="104" font-size="9" fill="var(--mut)" text-anchor="middle">'+'MTWTFSS'[i]+'</text>'});
 $('trendSvg').innerHTML=h+'<line x1="14" x2="290" y1="18" y2="18" stroke="var(--mut)" stroke-dasharray="3 3"/>';
 $('trendMsg').textContent=ch<=-15?"Mom's activity is "+Math.abs(ch)+'% lower this week, consider checking in.':ch>=15?"Mom's activity is "+ch+'% higher this week.':"Mom's activity is steady this week ("+(ch>0?'+':'')+ch+'% vs last week).'}
function nb(){try{return JSON.parse(ls.get('cr_nb'))}catch(e){return null}}
function nbLoad(){const o=nb();if(o){$('nbName').value=o.n;$('nbPhone').value=o.p;$('nbState').textContent='Emergency alerts also go to '+o.n+' ('+o.p+').'}}
$('nbSave').onclick=()=>{const n=$('nbName').value.trim(),p=$('nbPhone').value.trim().replace(/[\s-]/g,'');if(!n||!/^\+\d{8,15}$/.test(p)){$('nbState').textContent='Enter a name and a number like +918792340621.';return}ls.set('cr_nb',JSON.stringify({n,p}));nbLoad()};
const _s=sos;sos=function(l){_s(l);const o=nb();if(l==3)$('sosNote').textContent+=o?' '+o.n+' ('+o.p+') is also being alerted (demo).':' Add a neighbor in Emergency contacts so they are alerted too.'};
const ES=t=>{$('echoState').textContent=t};
function echoReply(){if(!et)return;clearInterval(et);et=null;$('echoBar').style.width='0';ES('Mom replied. Alert cancelled. Thank you, Mom.');sp('Thank you, Mom.')}
function echoFail(){clearInterval(et);et=null;ES('No reply. Notifying Priya and the neighbor.');sos(1);const o=nb();$('sosNote').textContent+=o?' '+o.n+' ('+o.p+') is also being notified (demo).':' Add a neighbor in Emergency contacts.'}
$('echoGo').onclick=()=>{clearInterval(et);ES('Echo asks: "Mom, are you okay? Please say yes."');sp('Mom, are you okay? Please say yes or tap I am fine.');let n=100;et=setInterval(()=>{n--;$('echoBar').style.width=n+'%';if(n<=0)echoFail()},100)};
$('echoOk').onclick=echoReply;
$('echoMic').onclick=()=>{const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR){ES('Voice recognition is not supported in this browser. Tap I am fine.');return}const r=new SR();r.lang='en-IN';r.onresult=e=>{if(/yes|fine|ok|okay|haan|theek/i.test(e.results[0][0].transcript))echoReply()};try{r.start()}catch(x){}};
const _r4=render;render=function(){_r4();batt();trend();applyView()};
const _sd2=setDay;setDay=function(i){spokenB={};_sd2(i)};
setPriv(privOn);consentUI();nbLoad();if(!ls.get('cr_consent'))showModal();render();
})();
