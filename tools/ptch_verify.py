#!/usr/bin/env python3
"""Checks skcore_note end to end: measured pitch of the dominant partial vs requested note."""
import numpy as np, glob, os, sys
sys.path.insert(0,'tools')
SR=44100; N=22050
def peak(x):
    seg=x[int(.03*SR):int(.25*SR)]
    if np.max(np.abs(seg))<1e-4: return None
    F=np.abs(np.fft.rfft(seg*np.hanning(len(seg)),1<<17)); fr=np.fft.rfftfreq(1<<17,1/SR); m=(fr>14)&(fr<8000)
    i=np.argmax(np.where(m,F,0)); return fr[i]
bad=0
for fn in sorted(glob.glob('out/ptchv/*.f32')):
    name=os.path.basename(fn)[:-4]; d=np.fromfile(fn,dtype=np.float32).reshape(-1,N)
    notes=[int(l) for l in open(fn[:-4]+'.txt')]
    err=[]
    for r,n in zip(d,notes):
        f=peak(r)
        if f: err.append(69+12*np.log2(f/440)-n)
    err=np.array(err); 
    print(f"{name:7s} notes {notes[0]}-{notes[-1]}  median err {np.median(err):+5.2f} st  max |err| {np.max(np.abs(err)):5.2f} st  within 1 st: {np.mean(np.abs(err)<=1)*100:3.0f}%")
