#!/usr/bin/env python3
"""Builds note->PTCH tables from out/ptch/analysis.json (run ptch_analyze.py first).
Writes data/ptch/<VOICE>.txt ("<midi note> <ptch>;" per line, Pd text format) and data/ptch/SUMMARY.md."""
import json, numpy as np, os
r=json.load(open('out/ptch/analysis.json')); os.makedirs('data/ptch',exist_ok=True)
def note(f): return 69+12*np.log2(f/440)
CLEAN_MIN_ST=2.0   # at least this many semitones of usable range
rows=[]
for n,d in sorted(r.items()):
    pts=[(v,note(f)) for v,f in d['table'] if f and f>14]
    # longest strictly rising run (allow 0.3 st wobble)
    best=[];cur=[]
    for v,s in pts:
        if cur and s>cur[-1][1]-0.3: cur.append((v,s))
        else:
            if len(cur)>len(best): best=cur
            cur=[(v,s)]
    if len(cur)>len(best): best=cur
    span=best[-1][1]-best[0][1] if len(best)>1 else 0
    if len(best)<8 or span<CLEAN_MIN_ST or d['tonality']<8:
        if d['slope']==0 or span<CLEAN_MIN_ST and d['mono']:
            kind='PTCH changes timbre, not the main partial'
        else: kind='unpitched / unstable (noise or partial switching)'
        rows.append((n,kind,None,None,None)); continue
    v=np.array([b[0] for b in best],float); s=np.array([b[1] for b in best])
    s=np.maximum.accumulate(s)
    lo,hi=s[0],s[-1]; frac=len(best)/len(pts)
    kind='clean' if (frac>0.9 and d['resid']<1.0) else 'partly pitched (jumps outside range)'
    lines=[]
    for m in range(0,128):
        if m<=lo: p=v[0] if m>=lo-0.5 else None
        elif m>=hi: p=v[-1] if m<=hi+0.5 else None
        else: p=np.interp(m,s,v)
        if p is not None: lines.append(f"{m} {int(round(p))};")
    open(f"data/ptch/{n}.txt",'w').write("\n".join(lines)+"\n")
    rows.append((n,kind,(lo,hi),(v[0],v[-1]),len(lines)))
md=["# PTCH measurements","","Dominant partial 30-250 ms after trigger, controls at defaults, 44.1 kHz. Note numbers are MIDI (A4=69=440 Hz).","",
"| Voice | Result | Note range | PTCH range |","|---|---|---|---|"]
for n,k,nr,pr,c in rows:
    md.append(f"| {n} | {k} | "+(f"{nr[0]:.1f} - {nr[1]:.1f}" if nr else "-")+" | "+(f"{int(pr[0])} - {int(pr[1])}" if pr else "-")+" |")
open('data/ptch/SUMMARY.md','w').write("\n".join(md)+"\n"); print("\n".join(md))
