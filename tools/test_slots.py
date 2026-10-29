#!/usr/bin/env python3
"""Headless regression for bela/slot*.pd: every machine of every slot is selected and triggered in turn.
Pass: the selected slot produces sound, the other slots stay silent.  Needs: make (externals in out/), pd."""
import subprocess, re, sys, os
sys.path.insert(0,'tools')
import importlib.util
spec=importlib.util.spec_from_file_location("g","tools/gen_bela.py"); src=open("tools/gen_bela.py").read().replace("\nmain()\n","\n")
g={}; exec(compile(src,"gen_bela","exec"),g)
SLOTS=g["SLOTS"]; P=g["P"]
p=P("t",1400,2000)
lb=p.add("loadbang",10,10); dsp=p.add("; pd dsp 1",10,30,"msg"); p.con(lb,0,dsp,0)
env=[]
for k,(nm,pan,ms) in enumerate(SLOTS):
    r=p.add(f"r sk-in-{k}",10+k*150,60); s=p.add(f"slot{k+1}",10+k*150,90); p.con(r,0,s,0)
    e=p.add("env~ 2048 1024",10+k*150,120); pr=p.add(f"print E{k}",10+k*150,150)
    p.con(s,0,e,0); p.con(s,1,e,0); p.con(e,0,pr,0)
T=1500; i=0; plan=[]
for k,(nm,pan,ms) in enumerate(SLOTS):
    for m,name in enumerate(ms):
        t0=T+i*1200
        d1=p.add(f"del {t0}",10,200+i*12); mm=p.add(f"machine {m}",100,200+i*12,"msg"); sa=p.add(f"s sk-in-{k}",190,200+i*12)
        d2=p.add(f"del {t0+200}",300,200+i*12); nn=p.add("note 40 110",400,200+i*12,"msg"); sb=p.add(f"s sk-in-{k}",500,200+i*12)
        mk=p.add(f"MARK {k} {m} {name}",600,200+i*12,"msg"); pm=p.add("print",700,200+i*12)
        p.con(lb,0,d1,0); p.con(d1,0,mm,0); p.con(mm,0,sa,0); p.con(lb,0,d2,0); p.con(d2,0,nn,0); p.con(nn,0,sb,0)
        p.con(d2,0,mk,0); p.con(mk,0,pm,0)
        plan.append((k,m,name)); i+=1
qd=p.add(f"del {int(T+i*1200+1200)}",1200,10); qm=p.add("; pd quit",1200,40,"msg"); p.con(lb,0,qd,0); p.con(qd,0,qm,0)
os.makedirs("out/t",exist_ok=True)
open("out/t/allslots.pd","w").write("\n".join(p.lines(top=True))+"\n")
dur=(T+i*1200+1500)/1000
log=subprocess.run(["pd","-nogui","-nosound","-r","44100","-noprefs","-stderr","-path","out","-path","pd","-path","bela","-open","out/t/allslots.pd"],
    capture_output=True,text=True,timeout=dur+30) if False else None
try:
    cp=subprocess.run(["timeout","300","pd","-batch","-nogui","-nosound","-r","44100","-noprefs","-stderr","-path","out","-path","pd","-path","bela","-open","out/t/allslots.pd"],capture_output=True,text=True)
except Exception as ex: print(ex); sys.exit(1)
out=cp.stdout+cp.stderr
open("out/t/allslots.log","w").write(out)
bad=0; cur=None; peaks={}; 
for line in out.splitlines():
    m=re.match(r"print: MARK (\d+) (\d+) (\S+)",line)
    if m: cur=(int(m.group(1)),int(m.group(2)),m.group(3)); peaks[cur]=[0]*len(SLOTS); continue
    m=re.match(r"E(\d+): ([-\d.e]+)",line)
    if m and cur:
        k=int(m.group(1)); v=float(m.group(2)); peaks[cur][k]=max(peaks[cur][k],v)
for (k,mi,name),pk in peaks.items():
    own=pk[k]; other=max(pk[j] for j in range(len(SLOTS)) if j!=k)
    ok = own>40 and other<own-40
    if not ok: bad+=1
    print(f"slot{k+1} machine{mi} {name:6s} own={own:6.1f} dB  others={other:5.1f}  {'ok' if ok else 'FAIL'}")
errs=[l for l in out.splitlines() if re.search(r"error|couldn't|no method",l)]
print(f"{len(peaks)}/{len(plan)} machines measured, {bad} failures, {len(errs)} Pd errors")
for l in errs[:10]: print(l)
sys.exit(1 if bad or errs or len(peaks)!=len(plan) else 0)
