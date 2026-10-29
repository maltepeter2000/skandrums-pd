#!/usr/bin/env python3
"""Generates bela/slot1..8.pd (one slot = several machines, one active) and bela/slots-main.pd.
Slot inlet: machine <k> | note <n> <vel> | ctl <i> <0-127> | preset <p> | level <0-1> | pan <0-1> | choke | dump
Slot outlets: 0 audio L, 1 audio R, 2 info: machine <k> | values v0..vN | choke"""
import os, math
TUNED = set(f[:-4].replace("-","").lower() for f in os.listdir("data/ptch") if f.endswith(".txt"))
SLOTS = [  # (name, pan 0..1, machines)
 ("kick",  0.50, ["trxb2","trxbd","efmbd","pibd"]),
 ("snare", 0.45, ["trxsd","efmsd","pisd"]),
 ("clap",  0.55, ["trxcp","efmcp","trxrs","efmrs","pirs"]),
 ("chat",  0.35, ["trxch","efmhh","pihh"]),
 ("ohat",  0.65, ["trxoh","efmhh","pihh","picc"]),
 ("cym",   0.75, ["trxcy","efmcy","pirc","picc"]),
 ("tom",   0.25, ["trxxt","efmxt","pimt","trxxc","piml"]),
 ("perc",  0.60, ["trxcb","efmcb","trxcl","trxma","pima"]),
]
class P:
    def __init__(s, name=None, w=900, h=600): s.o=[]; s.c=[]; s.name=name; s.w=w; s.h=h
    def add(s, txt, x, y, kind="obj"): s.o.append((kind,x,y,txt)); return len(s.o)-1
    def sub(s, p, x, y): s.o.append(("sub",x,y,p)); return len(s.o)-1
    def con(s,a,o,b,i): s.c.append((a,o,b,i))
    def lines(s, top=False):
        L=[f"#N canvas 0 50 {s.w} {s.h} 12;" if top else f"#N canvas 0 50 {s.w} {s.h} {s.name} 0;"]
        for k,x,y,t in s.o:
            if k=="sub":
                L += t.lines(); L.append(f"#X restore {x} {y} pd {t.name};")
            else: L.append(f"#X {k} {x} {y} {esc(t)};")
        for a,o,b,i in s.c: L.append(f"#X connect {a} {o} {b} {i};")
        return L
def esc(t): return t.replace("\\","").replace(",", " \\,").replace(";"," \\;").replace("$","\\$")

def machine(slot, k, m):
    p=P(f"m{k}_{m}",780,640); tuned = m in TUNED
    inl=p.add("inlet",20,20); rt=p.add("route note choke ctl preset dump",20,55); p.con(inl,0,rt,0)
    tn=p.add("t l b b",20,100); p.con(rt,0,tn,0)
    pre=p.add("list prepend note",20,150); trim=p.add("list trim",20,180)
    voice=p.add(f"{m}~",20,330); sw=p.add("switch~",20,420)
    m1=p.add("1",100,150,"msg"); stop=p.add("stop",160,150,"msg"); dl=p.add("del 10",260,200)
    p.con(tn,0,pre,0); p.con(pre,0,trim,0); p.con(trim,0,voice,0)
    p.con(tn,1,m1,0); p.con(m1,0,sw,0); p.con(tn,2,stop,0); p.con(stop,0,dl,0)
    tc=p.add("t b b",260,100); ch=p.add("choke",330,150,"msg"); z=p.add("0",260,240,"msg")
    p.con(rt,1,tc,0); p.con(tc,1,ch,0); p.con(ch,0,voice,0); p.con(tc,0,dl,0); p.con(dl,0,z,0); p.con(z,0,sw,0)
    if tuned:
        r0=p.add("route 0",420,100); sb=p.add("- 64",420,130); mul=p.add("* 0.1875",420,160)
        tr=p.add("transpose $1",420,190,"msg"); cp=p.add("list prepend ctl",540,130); ct=p.add("list trim",540,160)
        p.con(rt,2,r0,0); p.con(r0,0,sb,0); p.con(sb,0,mul,0); p.con(mul,0,tr,0); p.con(tr,0,voice,0)
        p.con(r0,1,cp,0); p.con(cp,0,ct,0); p.con(ct,0,voice,0)
    else:
        cp=p.add("list prepend ctl",420,130); ct=p.add("list trim",420,160)
        p.con(rt,2,cp,0); p.con(cp,0,ct,0); p.con(ct,0,voice,0)
    key=f"s{slot}m{k}{m}"
    sk=p.add(f"skpreset {key}",560,240); td=p.add(f"text define -k {key}",660,240)
    p.con(rt,3,sk,1); p.con(sk,0,voice,0)
    dq=p.add("dump",160,200,"msg"); p.con(rt,4,dq,0); p.con(dq,0,voice,0)   # dump request -> voice
    rd=p.add("route done dump",300,360); p.con(voice,1,rd,0)
    z2=p.add("0",300,395,"msg"); p.con(rd,0,z2,0); p.con(z2,0,sw,0)
    p.con(voice,1,sk,0)   # all events to skpreset (it filters dump itself)
    ls=p.add("list split 1",420,400); pv=p.add("list prepend values",420,430); oi=p.add("outlet",420,520)
    p.con(rd,1,ls,0); p.con(ls,1,pv,0); p.con(pv,0,oi,0)
    p.con(sk,1,pv,0)
    ob=p.add("outlet~",20,520); p.con(voice,0,ob,0)
    lb=p.add("loadbang",150,420); zz=p.add("0",150,450,"msg"); p.con(lb,0,zz,0); p.con(zz,0,sw,0)
    return p, ob, oi

def slot(idx, name, pan, machines):
    n=len(machines); p=P(f"slot{idx}",1000,820)
    inl=p.add("inlet",20,20)
    rt=p.add("route machine note ctl preset level pan choke dump",20,55); p.con(inl,0,rt,0)
    ii=p.add("i",20,95); mi=p.add("clip 0 %d"%(n-1),20,120); tm=p.add("t b f f",20,150)
    p.con(rt,0,ii,0); p.con(ii,0,mi,0); p.con(mi,0,tm,0)
    tcur=p.add("t f f f f f",150,150); p.con(tm,2,tcur,0)     # right: distribute index first
    dmp=p.add("dump",60,190,"msg"); p.con(tm,0,dmp,0)         # then request values from new machine
    ann=p.add("list prepend machine",250,190); it=p.add("list trim",250,700); info=p.add("outlet",250,780); p.con(tm,1,ann,0); p.con(ann,0,it,0); p.con(it,0,info,0)
    rr=p.add("route "+" ".join(map(str,range(n))),20,330)
    def branch(port, sel, x, k):
        a=p.add(f"list prepend {sel}",x,230); b=p.add("list prepend",x,260)
        p.con(rt,port,a,0); p.con(a,0,b,0); p.con(tcur,k,b,1); p.con(b,0,rr,0)
    branch(1,"note",20,0); branch(2,"ctl",160,1); branch(3,"preset",300,2); branch(6,"choke",440,3); branch(7,"dump",560,4)
    p.con(dmp,0,p.add("list prepend",60,215),0); b=len(p.o)-1; p.con(tcur,4,b,1); p.con(b,0,rr,0)
    mix=p.add("*~ 1",20,560); minfo=p.add("list prepend",200,560); p.con(minfo,0,it,0)
    # info from machines: values lists
    for k,m in enumerate(machines):
        sp,ob,oi=machine(idx,k,m); s=p.sub(sp,20+k*110,420)
        p.con(rr,k,s,0); p.con(s,0,mix,0); p.con(s,1,minfo,0)
    # level / pan with 10 ms ramps
    lv=p.add("pack f 10",700,330); ll=p.add("line~",700,360); p.con(rt,4,lv,0); p.con(lv,0,ll,0)
    pn=p.add("t f f",800,330); cs=p.add("* 1.5708",800,360); co=p.add("cos",800,385); si=p.add("sin",880,385)
    pl=p.add("pack f 10",800,420); pr=p.add("pack f 10",880,420); ql=p.add("line~",800,450); qr=p.add("line~",880,450)
    p.con(rt,5,pn,0); p.con(pn,0,cs,0); p.con(cs,0,co,0); p.con(cs,0,si,0)
    p.con(co,0,pl,0); p.con(si,0,pr,0); p.con(pl,0,ql,0); p.con(pr,0,qr,0)
    # m*level*gain
    ml=p.add("*~",20,600); p.con(mix,0,ml,0); p.con(ll,0,ml,1)
    L=p.add("*~",20,650); R=p.add("*~",150,650); p.con(ml,0,L,0); p.con(ml,0,R,0); p.con(ql,0,L,1); p.con(qr,0,R,1)
    oL=p.add("outlet~",20,720); oR=p.add("outlet~",150,720); p.con(L,0,oL,0); p.con(R,0,oR,0)
    # initial level/pan on load
    lb=p.add("loadbang",700,20); t2=p.add("t b b",700,50)
    il=p.add("0.8",700,80,"msg"); ip=p.add("%g"%pan,790,80,"msg")
    p.con(lb,0,t2,0); p.con(t2,0,il,0); p.con(t2,1,ip,0); p.con(il,0,lv,0); p.con(ip,0,pn,0)
    return p

def main():
    os.makedirs("bela",exist_ok=True)
    for i,(nm,pan,ms) in enumerate(SLOTS,1):
        s=slot(i,nm,pan,ms)
        # fix initial messages: send level 0.7 and pan to own inlet after loadbang (done in main), so drop
        # drop loadbang with no connection
        open(f"bela/slot{i}.pd","w").write("\n".join(s.lines(top=True))+"\n")
    print("slots written")

# ---------------------------------------------------------------- pot pickup
def skpot():
    p=P("skpot",700,420)
    ip=p.add("inlet",20,20); it=p.add("inlet",260,20); ie=p.add("inlet",420,20)
    tp=p.add("t f f",20,60); sb=p.add("-",20,110); ab=p.add("abs",20,140); lt=p.add("< 9",20,170)
    sel=p.add("sel 1",20,200); one=p.add("1",20,230,"msg")
    g=p.add("spigot",120,260); h=p.add("spigot",120,300); out=p.add("outlet",120,340)
    p.con(ip,0,tp,0); p.con(tp,1,sb,0); p.con(sb,0,ab,0); p.con(ab,0,lt,0); p.con(lt,0,sel,0); p.con(sel,0,one,0); p.con(one,0,g,1)
    p.con(tp,0,g,0); p.con(g,0,h,0); p.con(h,0,out,0)
    tt=p.add("t f b",260,60); zero=p.add("0",300,110,"msg"); p.con(it,0,tt,0); p.con(tt,0,sb,1); p.con(tt,1,zero,0); p.con(zero,0,g,1)
    p.con(ie,0,h,1)
    return p

# ---------------------------------------------------------------- midi per slot
def midi_sub(k, n):
    """inlet: "<cc> <val>" ; outlet 0: slot message ; outlet 1: bang when a control (CC 16-23) changed"""
    p=P(f"midi{k+1}",800,420)
    i=p.add("inlet",20,20)
    ccs=[7,10,70,71]+list(range(16,24))
    rt=p.add("route "+" ".join(map(str,ccs)),20,60); p.con(i,0,rt,0)
    o=p.add("outlet",20,380); chg=p.add("outlet",700,380)
    def chain(port, items, x):
        prev=None
        for j,(kind,c) in enumerate(items):
            nid=p.add(c,x,110+j*40,kind)
            p.con(rt,port,nid,0) if prev is None else p.con(prev,0,nid,0)
            prev=nid
        p.con(prev,0,o,0)
    chain(0,[("obj","/ 127"),("msg","level $1")],20)
    chain(1,[("obj","/ 127"),("msg","pan $1")],120)
    chain(2,[("obj","* %d"%n),("obj","/ 128"),("obj","int"),("msg","machine $1")],220)
    chain(3,[("obj","/ 8"),("obj","int"),("msg","preset $1")],340)
    for j in range(8):
        chain(4+j,[("msg",f"ctl {j} $1")],440+j*40)
        tb=p.add("t b",440+j*40,200); p.con(rt,4+j,tb,0); p.con(tb,0,chg,0)
    return p

# ---------------------------------------------------------------- main
LEDS=[17,18,21,13,14,11,12,15,16,19]
BUTTONS=[26,25,24,23]
def build_main():
    NS=len(SLOTS); p=P("main",1500,1300)
    p.add("declare -path /root/Bela/projects/pd-externals/skandrums",20,10)
    p.add("array define sk-m %d"%NS,300,10); p.add("array define sk-n %d"%NS,300,40)
    lb=p.add("loadbang",20,40)
    init=p.add("out "+" \\, out ".join(map(str,LEDS))+" \\, in "+" \\, in ".join(map(str,BUTTONS)),20,70,"msg")
    sd=p.add("s bela_setDigital",20,100); p.con(lb,0,init,0); p.con(init,0,sd,0)
    cnt=p.add("; sk-n 0 "+" ".join(str(len(s[2])) for s in SLOTS),300,70,"msg")
    zm=p.add("; sk-m 0 "+" ".join("0" for s in SLOTS),300,100,"msg")
    p.con(lb,0,cnt,0); p.con(lb,0,zm,0)
    d1=p.add("del 300",150,40); z0=p.add("0",150,70,"msg"); s0=p.add("s sk-slot",150,100)
    p.con(lb,0,d1,0); p.con(d1,0,z0,0); p.con(z0,0,s0,0)
    # slots + master
    mixL=p.add("*~ 0.3",20,1000); mixR=p.add("*~ 0.3",140,1000); dac=p.add("dac~ 1 2",20,1050)
    p.con(mixL,0,dac,0); p.con(mixR,0,dac,1)
    slotid=[]
    for k in range(NS):
        x=20+k*130
        r=p.add(f"r sk-in-{k}",x,900); s=p.add(f"slot{k+1}",x,940)
        p.con(r,0,s,0); p.con(s,0,mixL,0); p.con(s,1,mixR,0); slotid.append(s)
    # to-current router
    rt=p.add("r sk-tocur",400,140); tt=p.add("t a b",400,170); vc=p.add("v sk-cur",480,200)
    lp=p.add("list prepend",400,230); rr=p.add("route "+" ".join(map(str,range(NS))),400,260)
    p.con(rt,0,tt,0); p.con(tt,1,vc,0); p.con(vc,0,lp,1); p.con(tt,0,lp,0); p.con(lp,0,rr,0)
    for k in range(NS):
        sn=p.add(f"s sk-in-{k}",400+k*80,300); p.con(rr,k,sn,0)
    # MIDI in
    ni=p.add("notein",700,40); npk=p.add("pack f f f",700,70); nm=p.add("$3 $1 $2",700,100,"msg"); ns=p.add("s sk-mnote",700,130)
    p.con(ni,0,npk,0); p.con(ni,1,npk,1); p.con(ni,2,npk,2); p.con(npk,0,nm,0); p.con(nm,0,ns,0)
    ci=p.add("ctlin",900,40); cpk=p.add("pack f f f",900,70); cm=p.add("$3 $2 $1",900,100,"msg"); cs=p.add("s sk-mcc",900,130)
    p.con(ci,0,cpk,0); p.con(ci,1,cpk,1); p.con(ci,2,cpk,2); p.con(cpk,0,cm,0); p.con(cm,0,cs,0)
    rn=p.add("r sk-mnote",700,180); rch=p.add("route "+" ".join(str(i+1) for i in range(NS)),700,210); p.con(rn,0,rch,0)
    for k in range(NS):
        nm2=p.add("note $1 $2",700+(k%4)*110,250+(k//4)*60,"msg"); sk_=p.add(f"s sk-in-{k}",700+(k%4)*110,280+(k//4)*60)
        p.con(rch,k,nm2,0); p.con(nm2,0,sk_,0)
    ch=p.add("choke",1150,250,"msg"); cs2=p.add("s sk-in-4",1150,280); p.con(rch,3,ch,0); p.con(ch,0,cs2,0)
    rc=p.add("r sk-mcc",900,350); rcc=p.add("route "+" ".join(str(i+1) for i in range(NS)),900,380); p.con(rc,0,rcc,0)
    for k in range(NS):
        sub=p.sub(midi_sub(k,len(SLOTS[k][2])),900+(k%4)*110,420+(k//4)*60)
        sk_=p.add(f"s sk-in-{k}",900+(k%4)*110,480+(k//4)*60)
        p.con(rcc,k,sub,0); p.con(sub,0,sk_,0)
        kc=p.add(str(k),1330,420+k*25,"msg"); sc=p.add("s sk-chg",1380,420+k*25); p.con(sub,1,kc,0); p.con(kc,0,sc,0)
    # CC on the selected slot -> re-read values after 80 ms
    rg=p.add("r sk-chg",1250,640); tg=p.add("t f b",1250,670); vg=p.add("v sk-cur",1300,700); eq=p.add("==",1250,730)
    sl=p.add("sel 1",1250,760); dl=p.add("del 80",1250,790); dm=p.add("dump",1250,820,"msg"); st=p.add("s sk-tocur",1250,850)
    p.con(rg,0,tg,0); p.con(tg,1,vg,0); p.con(vg,0,eq,1); p.con(tg,0,eq,0); p.con(eq,0,sl,0); p.con(sl,0,dl,0); p.con(dl,0,dm,0); p.con(dm,0,st,0)
    # buttons (value 0 = pressed)
    ev=[]
    for b,pin in enumerate(BUTTONS):
        r=p.add(f"r bela_digitalIn{pin}",20+b*170,160); sl_=p.add("sel 0",20+b*170,190); p.con(r,0,sl_,0); ev.append(sl_)
    def nav(sl_, add, x):
        t1=p.add("t b",x,230); v=p.add("v sk-cur",x,260); a=p.add(f"+ {add}",x,290); m=p.add("mod %d"%NS,x,320)
        t2=p.add("t f f",x,350); v2=p.add("v sk-cur",x+70,380); s=p.add("s sk-slot",x,410)
        p.con(sl_,0,t1,0); p.con(t1,0,v,0); p.con(v,0,a,0); p.con(a,0,m,0); p.con(m,0,t2,0); p.con(t2,1,v2,0); p.con(t2,0,s,0)
    nav(ev[0],NS-1,20); nav(ev[1],1,180)
    def mnav(sl_, d, x):
        t1=p.add("t b",x,230); v=p.add("v sk-cur",x,260); t3=p.add("t f f f",x,290)
        tn=p.add("tabread sk-n",x+110,330); tm=p.add("tabread sk-m",x,330); ad=p.add(f"+ {d}",x,360)
        pl=p.add("+",x,390); md=p.add("mod",x,420); t4=p.add("t f f f",x,450)
        tw=p.add("tabwrite sk-m",x,490); ms=p.add("machine $1",x+90,490,"msg"); tc=p.add("s sk-tocur",x+90,520)
        bs=p.add("+ 1",x+180,490); bt=p.add("s sk-bar",x+180,520)
        p.con(sl_,0,t1,0); p.con(t1,0,v,0); p.con(v,0,t3,0)
        p.con(t3,2,tw,1); p.con(t3,1,tn,0); p.con(t3,0,tm,0)
        p.con(tn,0,pl,1); p.con(tn,0,md,1); p.con(tm,0,ad,0); p.con(ad,0,pl,0); p.con(pl,0,md,0); p.con(md,0,t4,0)
        p.con(t4,2,tw,0); p.con(t4,1,ms,0); p.con(ms,0,tc,0); p.con(t4,0,bs,0); p.con(bs,0,bt,0)
    mnav(ev[2],-1,340); mnav(ev[3],1,560)
    # slot change -> new slot dumps its values
    r1=p.add("r sk-slot",20,560); dd=p.add("dump",20,590,"msg"); tc2=p.add("s sk-tocur",20,620); p.con(r1,0,dd,0); p.con(dd,0,tc2,0)
    # LEDs
    rs=p.add("r sk-slot",20,660); rb=p.add("r sk-bar",200,660)
    ts=p.add("t "+" ".join(["f"]*8),20,690); tb=p.add("t "+" ".join(["f"]*8),200,690)
    p.con(rs,0,ts,0); p.con(rb,0,tb,0)
    for j in range(8):
        e=p.add(f"== {j}",20+j*70,720); g=p.add(f"> {j}",20+j*70+30,745); so=p.add(f"s bela_digitalOut{LEDS[j]}",20+j*70,780)
        p.con(ts,j,e,0); p.con(e,0,so,0); p.con(tb,j,g,0); p.con(g,0,so,0)
    bd=p.add("del 700",380,660); bv=p.add("v sk-cur",380,690); p.con(rb,0,bd,0); p.con(bd,0,bv,0); p.con(bv,0,ts,0)
    # selected slot's values -> pot targets/enable
    vals=p.add("list prepend",1000,540)
    for k in range(NS):
        x=20+k*125
        rv=p.add("route values",x,830); spg=p.add("spigot",x,860)
        rg2=p.add("r sk-slot",x+55,800); eq2=p.add(f"== {k}",x+55,830)
        p.con(slotid[k],2,rv,0); p.con(rv,0,spg,0); p.con(rg2,0,eq2,0); p.con(eq2,0,spg,1); p.con(spg,0,vals,0)
    tl=p.add("t l l",1000,570); p.con(vals,0,tl,0)
    un=p.add("unpack f f f f f f f f",1000,600); p.con(tl,0,un,0)
    ln=p.add("list length",1250,600); p.con(tl,1,ln,0)
    tn8=p.add("t "+" ".join(["f"]*8),1250,630); p.con(ln,0,tn8,0)
    # pots: adc~ 3..10
    adc=p.add("adc~ 3 4 5 6 7 8 9 10",1000,250)
    mt=p.add("metro 10",1300,250); tb8=p.add("t "+" ".join(["b"]*8),1300,280); lb2=p.add("loadbang",1300,220)
    p.con(lb2,0,mt,0); p.con(mt,0,tb8,0)
    for j in range(8):
        x=1000+(j%4)*120; y=310+(j//4)*120
        sn=p.add("snapshot~",x,y); sc=p.add("* 127",x,y+25); cl=p.add("clip 0 127",x,y+50); it=p.add("int",x,y+75)
        chg=p.add("change",x+45,y+75)
        p.con(adc,j,sn,0); p.con(tb8,j,sn,0); p.con(sn,0,sc,0); p.con(sc,0,cl,0); p.con(cl,0,it,0); p.con(it,0,chg,0)
        pot=p.add("skpot",x,y+100); cm_=p.add(f"ctl {j} $1",x,y+125,"msg"); sc2=p.add("s sk-tocur",x,y+150)
        p.con(chg,0,pot,0); p.con(un,j,pot,1); p.con(tn8,j,gt:=p.add(f"> {j}",x+60,y+100),0); p.con(gt,0,pot,2)
        p.con(pot,0,cm_,0); p.con(cm_,0,sc2,0)
    return p

def main():
    os.makedirs("bela",exist_ok=True)
    for i,(nm,pan,ms) in enumerate(SLOTS,1):
        open(f"bela/slot{i}.pd","w").write("\n".join(slot(i,nm,pan,ms).lines(top=True))+"\n")
    open("bela/skpot.pd","w").write("\n".join(skpot().lines(top=True))+"\n")
    open("bela/_main.pd","w").write("\n".join(build_main().lines(top=True))+"\n")
    print("bela/: slot1-%d.pd, skpot.pd, _main.pd"%len(SLOTS))
main()
