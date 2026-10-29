#!/usr/bin/env python3
"""Generate tests/pd/test_events.pd: choke wiring, dump/restore, errors."""
objs, conns = [], []
def add(s): objs.append(s); return len(objs) - 1
def conn(a, ao, b, bi): conns.append(f"#X connect {a} {ao} {b} {bi};")
SEMI = chr(92) + ";"
lb  = add("#X obj 10 10 loadbang;")
rch = add("#X obj 300 10 r ch;")
roh = add("#X obj 420 10 r oh;")
rcm = add("#X obj 540 10 r cmd;")
ch  = add("#X obj 300 100 trxch~;")
oh  = add("#X obj 420 100 trxoh~;")
pch = add("#X obj 300 150 print CH;")
poh = add("#X obj 450 150 print OH;")
wr  = add("#X obj 420 200 writesf~ 1;")
dac = add("#X obj 420 230 dac~;")
conn(rch, 0, ch, 0); conn(roh, 0, oh, 0); conn(rcm, 0, wr, 0)
conn(ch, 1, oh, 0); conn(ch, 1, pch, 0); conn(oh, 1, poh, 0)
conn(oh, 0, wr, 0); conn(oh, 0, dac, 0)
sched = [
 (0,    "; pd dsp 1; cmd open -bytes 4 /tmp/oh_test.wav; cmd start"),
 (50,   "; oh bang"),
 (400,  "; ch bang"),
 (900,  "; oh bang"),
 (1000, "; oh dump; oh get dec; oh dec 10; oh dump; oh dump trxoh 1 2 3 4 5; oh dump; ch dump"),
 (1100, "; oh dump trxch 1 2 3 4 5; oh dump trxoh 7 8 9 10 11; oh dump; oh foo; oh dec abc; oh ctl 9 1"),
 (1200, "; oh print; oh 200; oh choke; oh chokems 20; oh bang; oh level 0.5"),
 (2500, "; cmd stop"),
 (2600, "; pd quit"),
]
for i, (t, m) in enumerate(sched):
    d  = add(f"#X obj 10 {50 + i*40} delay {t};")
    mm = add(f"#X msg 10 {70 + i*40} " + m.replace(";", " " + SEMI + " ") + ";")
    conn(lb, 0, d, 0); conn(d, 0, mm, 0)
with open("tests/pd/test_events.pd", "w") as f:
    f.write("#N canvas 0 50 700 500 10;\n")
    f.write("\n".join(objs) + "\n" + "\n".join(conns) + "\n")
