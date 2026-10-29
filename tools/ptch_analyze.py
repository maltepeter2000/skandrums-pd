#!/usr/bin/env python3
"""Reads out/ptch/*.f32 and prints, per voice, the dominant frequency vs. PTCH (MIDI note), tonality and slope."""
import numpy as np, glob, os, sys, json
SR=44100; N=22050
def peak(x, a, b):
    seg=x[int(a*SR):int(b*SR)]
    if np.max(np.abs(seg))<1e-4: return None,0
    w=np.hanning(len(seg)); F=np.abs(np.fft.rfft(seg*w, 1<<17))
    fr=np.fft.rfftfreq(1<<17,1/SR); m=(fr>20)&(fr<8000)
    i=np.argmax(np.where(m,F,0)); 
    if 0<i<len(F)-1:
        a_,b_,c_=np.log(F[i-1]+1e-12),np.log(F[i]+1e-12),np.log(F[i+1]+1e-12)
        d=0.5*(a_-c_)/(a_-2*b_+c_); f=fr[i]+d*(fr[1]-fr[0])
    else: f=fr[i]
    ton=F[i]/(np.sqrt(np.mean(F[m]**2))+1e-12)
    return f,ton
def note(f): return 69+12*np.log2(f/440)
res={}
for fn in sorted(glob.glob('out/ptch/*.f32')):
    name=os.path.basename(fn)[:-4]
    d=np.fromfile(fn,dtype=np.float32).reshape(-1,N)
    vals=[p*4 for p in range(32)][:d.shape[0]-0]
    vals=list(range(0,124,4))+[124,127]; vals=vals[:d.shape[0]] if d.shape[0]<len(vals) else vals
    vals=[min(v,127) for v in (list(range(0,128,4))[:32])]
    rows=[]
    for r,v in zip(d,vals):
        f,t=peak(r,0.03,0.25)
        rows.append((v,f,t))
    ok=[(v,note(f)) for v,f,t in rows if f]
    if len(ok)>4:
        x=np.array([o[0] for o in ok]); y=np.array([o[1] for o in ok])
        s,c=np.polyfit(x,y,1); resid=np.std(y-(s*x+c))
        mono=np.all(np.diff(y)>-0.5)
    else: s=c=resid=0; mono=False
    tons=np.median([t for v,f,t in rows if f]) if ok else 0
    res[name]=dict(slope=s,icpt=c,resid=resid,mono=bool(mono),tonality=float(tons),
        table=[(v,None if f is None else round(float(f),1)) for v,f,t in rows])
    sel=[r for r in rows if r[0] in (0,32,64,96,124)]
    print(f"{name:7s} tonal={tons:6.1f} slope={s:5.2f} st/step resid={resid:5.1f}st mono={mono}  "+"  ".join(f"{v}:{'-' if f is None else round(f)}Hz" for v,f,t in sel))
json.dump(res,open('out/ptch/analysis.json','w'),indent=1)
