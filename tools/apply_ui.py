"""Apply the CareRing UI upgrade to web/index.html (idempotent, keeps a .bak).
Adds: cultural routine engine, reverse check-in, animations, 3 extra scenarios, medicine and meal schedule.
Usage:  python tools/apply_ui.py"""
import subprocess, sys, shutil
P = "web/index.html"
h = open(P, encoding="utf-8").read()
def R(a, b):
    global h
    if a not in h: sys.exit("Patch point not found, nothing written:\n  " + a[:70])
    h = h.replace(a, b, 1)
if "calRow" not in h:
    R("</style>", r"""@keyframes up{from{opacity:0;transform:translateY(14px)}}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(217,130,43,.5)}100%{box-shadow:0 0 0 14px rgba(217,130,43,0)}}
@keyframes bob{50%{transform:translateY(-4px) rotate(10deg)}}
@keyframes grow{from{transform:scaleX(0)}}
@keyframes rip{0%{box-shadow:0 0 0 0 rgba(194,65,12,.6)}100%{box-shadow:0 0 0 24px rgba(194,65,12,0)}}
.card{animation:up .5s both}.ins{animation:pulse 1.6s 2}.act .dot{animation:pulse 1.2s infinite}
#tl rect{transform-box:fill-box;transform-origin:left;animation:grow .8s both}#tl circle{animation:up .6s both}
button{transition:transform .15s}button:active{transform:scale(.95)}
.sos{font-size:16px;padding:14px 18px;border-color:var(--acc);animation:rip 2.2s infinite}.sos.hot{background:var(--bad);color:#fff;border-color:var(--bad)}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style>""")
    R("<h1>💍 CareRing</h1>", '<h1><span style="display:inline-block;animation:bob 3s infinite">💍</span> CareRing</h1>')
    R("if(d.kitchen===null){", "if(d.kitchen===null&&cal!='ramadan'&&cal!='diwali'){")
    R("else if(Math.abs(d.kitchen-bk)", "else if(d.kitchen!==null&&Math.abs(d.kitchen-bk)")
    R("if(cOut.checked&&d.out===null){", "if((cOut.checked||cal=='temple')&&cal!='diwali'&&d.out===null){")
    R("score=Math.max(0,score);return", "if(cal!='everyday')f.push({t:'Cultural routine applied: '+CALS[cal][0]+'. '+CALS[cal][1],sev:0,good:1});score=Math.max(0,score);return")
    R('`<div class="ins">${x.t}</div>`', '`<div class="ins${x.good?\' good\':\'\'}">${x.t}</div>`')
    R("score.textContent=sc;", "countUp(sc);")
    R("if(!sev){esc.innerHTML", "if(!sev&&escState<0){esc.innerHTML")
    R("if(!analyze().f.length)return;", "if(!analyze().f.filter(x=>x.sev).length)return;")
    R('<text x="${X(NOW)+3}"', '<circle cx="${X(NOW)}" cy="12" r="4" fill="var(--bad)"><animate attributeName="r" values="3;8;3" dur="1.6s" repeatCount="indefinite"/></circle><text x="${X(NOW)+3}"')
    R("<script>\n", r"""<script>
const API='API_BASE_PLACEHOLDER',live=!API.startsWith('API_');
const CALS={everyday:['Everyday','Standard routine.'],ramadan:['Ramadan','Pre-dawn kitchen activity is normal. Morning kitchen check paused.'],temple:['Sunday temple','A temple outing by 10 AM is expected.'],diwali:['Diwali','Festival day: visitors and cooking all day. Outing and kitchen checks paused.']};
let cal='everyday',_sc=0;
""")
    R("</script></body></html>", r"""
function countUp(t){const el=document.getElementById('score'),f=_sc;_sc=t;const s=performance.now();(function st(n){const p=Math.min(1,(n-s)/700);el.textContent=Math.round(f+(t-f)*p);if(p<1)requestAnimationFrame(st)})(s)}
function renderCal(){calRow.innerHTML=Object.keys(CALS).map(k=>`<button class="${k==cal?'on':''}" onclick="setCal('${k}')">${CALS[k][0]}</button>`).join('');calNote.textContent=CALS[cal][1]}
function showLive(d){const el=document.getElementById('liveBody');if(!el||!d.msg)return;const m=document.createElement('div');m.className='ins';m.textContent=d.msg;const s=document.createElement('div');s.textContent='Source: '+({ai:'Claude on Amazon Bedrock',help:'Mom pressed the help button'}[d.source]||'rule-based fallback')+' | '+new Date(d.ts*1000).toLocaleString()+' | '+(d.ack?'Mom replied':'awaiting reply');el.textContent='';el.appendChild(m);el.appendChild(s)}
function setCal(k){cal=k;renderCal();render();if(live)fetch(API+'?action=mode&elder=mom&value='+k).then(r=>r.json()).then(showLive).catch(()=>{})}
function sos(l){sosNote.textContent=l==1?'Priya has been notified. Help is on the way.':'Emergency sent to the whole care circle.';sosNote.className='sm bad';
 if(live)fetch(API+'?action=help&elder=mom&level='+l).then(r=>r.json()).then(showLive).catch(()=>{});
 resetEsc();escState=l==3?3:0;render();
 if(l==1)[1,2,3].forEach((x,i)=>timers.push(setTimeout(()=>{if(!replied){escState=x;render()}},(i+1)*1800)))}
document.querySelectorAll('.card').forEach((c,i)=>c.style.animationDelay=i*.07+'s');renderCal();render();
</script></body></html>""")
    try:
        u = subprocess.check_output(["aws","cloudformation","describe-stacks","--stack-name","carering","--query","Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue","--output","text"], text=True).strip()
        if u.startswith("http"): h = h.replace("API_BASE_PLACEHOLDER", u)
    except Exception as e: print("Could not read ApiUrl (calendar and help will run offline):", e)
    CARDS = """<div class="card"><h2>Cultural routine engine</h2><div class="row" id="calRow"></div><div class="sm" id="calNote" style="margin-top:8px"></div></div>
<div class="card"><h2>Reverse check-in · Mom's view</h2><div class="row"><button class="sos" onclick="sos(1)">🙋 I need Priya</button><button class="sos hot" onclick="sos(3)">🚨 Emergency</button></div><div class="sm" id="sosNote" style="margin-top:10px">Mom can ask for help herself. One tap, no watching involved.</div></div>
"""
else: CARDS = ""
if "schedList" not in h:
    CARDS += """<div class="card"><h2>Medicine and meal schedule</h2><div class="sm" id="simLbl"></div><input type="range" id="simSl" min="360" max="1380" step="15" value="665" style="width:100%"><div id="schedAlert"></div><div id="schedList"></div><div class="sm" style="margin-top:8px">Drag the slider to move the clock. Meals are checked against kitchen activity. Tablets need a tap. Reminders are spoken aloud.</div></div>
"""
    SCHED = open(__file__.replace("apply_ui.py","sched_module.js"), encoding="utf-8").read()
    R("</script></body></html>", SCHED + "</script></body></html>")
if CARDS: R('<div class="card"><h2>Family settings</h2>', CARDS + '<div class="card"><h2>Family settings</h2>')
shutil.copy(P, P + ".bak"); open(P, "w", encoding="utf-8").write(h); print("Done. Backup saved as web/index.html.bak")
