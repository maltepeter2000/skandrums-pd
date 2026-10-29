#!/usr/bin/env python3
"""Generate the help patches (<name>~-help.pd) for all voices.

usage: gen_help.py voices.txt outdir [name ...]

voices.txt comes from tools/dump_voices.c (make help does both).
Layout grid: M = 20 px margin. See the constants below.
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manual_text

BS = chr(92)
SEMI, COMMA, DOLLAR, SPACE = BS + ";", BS + ",", BS + "$", BS + " "

# ---- grid -------------------------------------------------------------
M = 20                        # margin unit
YEL_X, YEL_Y, YEL_W = 2 * M, M, 700        # writing surface (yellow)
PINK_X, PINK_W = M, M                      # pink strip left of it
PINK_TOP = YEL_Y + 3 * M                   # staggered starts
BLUE_W = 200                               # blue panel, overhangs by M
BLUE_X = YEL_X + YEL_W + M - BLUE_W
BLUE_TOP = PINK_TOP + 3 * M
CX = YEL_X + M                             # x of all heading squares
LBL = 24                                   # label offset right of a square
TX = CX + LBL - 2                          # x of comment blocks (text starts +2)
LINE = 16                                  # line height of font 12
MAXCH = 62                                 # max characters per comment line
PINK, YELLOW, BLUE = "#ffcfd6", "#fafaf2", "#1e3791"

ROLES = {
    "trx": {"bd": "Bass Drum", "b2": "Bass Drum 2", "sd": "Snare", "xt": "Extra Tom",
            "xc": "Extra Conga", "cp": "Clap", "rs": "Rimshot", "cb": "Cowbell",
            "cl": "Claves", "ch": "Closed Hat", "oh": "Open Hat", "cy": "Cymbal",
            "ma": "Maracas"},
    "efm": {"bd": "Bass Drum", "sd": "Snare", "xt": "Extra Tom", "cp": "Clap",
            "rs": "Rimshot", "cb": "Cowbell", "hh": "Hi-Hat", "cy": "Cymbal"},
    "pi": {"bd": "Bass Drum", "sd": "Snare", "mt": "Tom", "ml": "Metallica",
           "ma": "Maracas", "rs": "Rimshot", "hh": "Hi-Hat", "rc": "Ride",
           "cc": "Crash"},
}


def esc(s):
    """Escape a comment/message text for a .pd file."""
    return (s.replace(",", " " + COMMA).replace(";", SEMI).replace("$", DOLLAR))


def label(s):
    return s.replace(" ", SPACE)


class Patch:
    def __init__(self):
        self.lines, self.conns, self.n = [], [], 0

    def add(self, text):
        self.lines.append(text)
        self.n += 1
        return self.n - 1

    def conn(self, a, ao, b, bi):
        self.conns.append(f"#X connect {a} {ao} {b} {bi};")

    def cnv(self, x, y, w, h, lbl="empty", xo=20, yo=12, fs=30, bg=YELLOW, sel=19):
        return self.add(f"#X obj {x} {y} cnv {sel} {w} {h} empty empty {lbl} {xo} {yo} 0 {fs} {bg} #000000 0;")

    def heading(self, x, y, text, fs):
        return self.cnv(x, y, 10, 10, label(text), LBL, 6, fs, BLUE, 10)

    def comment(self, x, y, lines, width=MAXCH + 2):
        """One text; every line break is a semicolon (Pd shows it at line end)."""
        for ln in lines:
            assert len(ln) <= MAXCH, f"line too long ({len(ln)}): {ln}"
        body = (" " + SEMI + " ").join(esc(l) for l in lines)
        return self.add(f"#X text {x} {y} {body}, f {width};")


def wrap(text, width=MAXCH):
    out, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + [cur]


def build(name, fam, code, ctls):
    short = fam + code
    obj = short + "~"
    role = ROLES[fam][code]
    p = Patch()
    n = len(ctls)

    # --- layout numbers (all derived, nothing hand-placed) ---
    rows = math.ceil(n / 4)
    synth, quote = manual_text.FAMILY[fam]
    top_y = YEL_Y + 3 * M + 24 + 28   # metro toggle
    util_y = top_y + 66                           # utility row
    ctl_y0 = util_y + 56
    ROW = 90                                      # pitch of the control rows
    last_s = ctl_y0 + ROW * (rows - 1) + 58       # y of the last [s] box
    r_y = last_s + 18 + 20
    obj_y = r_y + 36
    mul_y, dac_y = obj_y + 36, obj_y + 72
    y = mul_y + 66 + 18 + 36    # first text section

    sections = []
    sections.append(("Inlets", ["0: messages (see Messages below)"]))
    sections.append(("Outlets", ["0: signal (mono)",
                                 "1: events: choke, done, value, dump"]))
    sections.append(("Messages", [
        "bang, <1-127>: trigger, the number is the velocity",
        "<control> <0-127>: set a control by name, e.g. " + ctls[0][0].lower() + " 64",
        "ctl <index> <0-127>, params v0 v1 ...: set by index",
        "defaults, reset: default controls, restart the voice",
        "level <0-8>: output gain, default 1",
        "get <control>: reply 'value <control> <v>' on outlet 1",
        "print: voice, controls and sample rate to the Pd window",
        "choke, chokems <ms>: fade the voice out, default 3 ms",
        "store <0-15>, recall <0-15>: 16 internal slots",
        "dump, dump <0-15>: send all controls to outlet 1",
        "dump " + short + " v0 v1 ...: restore a dump of this voice"]))
    man = manual_text.PARAMS.get(short, {})
    clines = []
    for i, (cn, dv) in enumerate(ctls):
        ln = f"{i} {cn.lower()} ({dv})"
        if cn in man:
            ln += ": " + man[cn]
        clines += wrap(ln)
    sections.append(("Controls (index name default)", clines))
    sections.append(("Choke and presets", [
        "Outlet 1 sends 'choke' at every trigger. Connect it to the",
        "inlet of another voice to cut that voice off, e.g.",
        "[trxch~] outlet 1 -> [trxoh~] inlet.",
        "'dump' sends 'dump " + short + " v0 v1 ...' to outlet 1 - keep it in",
        "[text define -k] and send it back to restore the controls."]))

    placed = []
    for title, lines in sections:
        placed.append((title, lines, y))
        y += 24 + LINE * len(lines) + 28
    credits_y = y
    yel_bottom = credits_y + 3 * LINE + M
    bar_bottom = yel_bottom + M

    # --- background and bars (z-order: yellow, pink, blue) ---
    p.cnv(YEL_X, YEL_Y, YEL_W, yel_bottom - YEL_Y, bg=YELLOW)
    p.cnv(PINK_X, PINK_TOP, PINK_W, bar_bottom - PINK_TOP, bg=PINK)
    p.cnv(BLUE_X, BLUE_TOP, BLUE_W, bar_bottom - BLUE_TOP, bg=BLUE)

    # --- title and description ---
    p.heading(CX, YEL_Y + M, obj, 22)
    p.heading(CX, YEL_Y + 3 * M, f"{role} ({fam.upper()}-{code.upper()}) - {synth}", 16)

    # --- example patch: every message row ends in its own [s], one [r] feeds the object ---
    bus = DOLLAR + "0-" + short
    o = p.add(f"#X obj {CX} {obj_y} {obj};")
    rcv = p.add(f"#X obj {CX} {r_y} r {bus};")
    p.conn(rcv, 0, o, 0)
    snd0 = p.add(f"#X obj {CX} {util_y + 30} s {bus};")
    tgl = p.add(f"#X obj {CX} {top_y} tgl 19 0 empty empty empty 0 -10 0 12 #fcfcfc #000000 #000000 0 1;")
    met = p.add(f"#X obj {CX} {top_y + 28} metro 500;")
    p.conn(tgl, 0, met, 0)
    p.conn(met, 0, snd0, 0)
    bng = p.add(f"#X obj {CX + 6} {util_y} bng 19 250 50 0 empty empty empty 17 7 0 10 #fcfcfc #000000 #000000;")
    p.conn(bng, 0, snd0, 0)
    vel = p.add(f"#X msg {CX + 41} {util_y} 100;")
    p.conn(vel, 0, snd0, 0)
    x = CX + 100
    for text in ("dump", "defaults", "choke", "print", "store 0", "recall 0"):
        m = p.add(f"#X msg {x} {util_y} {text};")
        p.conn(m, 0, snd0, 0)
        x += 7 * len(text) + 4 + 16
    snds = {}
    atoms = []
    for i, (cname, _) in enumerate(ctls):
        r, c = divmod(i, 4)
        cx = CX + c * 112
        ay = ctl_y0 + ROW * r
        if r not in snds:
            snds[r] = p.add(f"#X obj {CX} {ay + 58} s {bus};")
        a = p.add(f"#X floatatom {cx} {ay} 4 0 127 0 - {DOLLAR}0-c{i} -;")
        atoms.append(a)
        m = p.add(f"#X msg {cx} {ay + 30} {cname.lower()} {DOLLAR}1;")
        p.conn(a, 0, m, 0)
        p.conn(m, 0, snds[r], 0)
    mul = p.add(f"#X obj {CX} {mul_y} *~ 0.3;")
    dac = p.add(f"#X obj {CX} {dac_y} dac~;")
    pr = p.add(f"#X obj {CX + 330} {mul_y} print {short.upper()};")
    rt = p.add(f"#X obj {CX + 110} {mul_y} route params;")
    n = len(ctls)
    up = p.add(f"#X obj {CX + 110} {mul_y + 30} unpack {' '.join(['f'] * n)};")
    p.conn(rt, 0, up, 0)
    for i in range(n):       # feed the number boxes back through their receive names
        sx = p.add(f"#X obj {CX + 62 * i} {mul_y + 66} s {DOLLAR}0-c{i};")
        p.conn(up, i, sx, 0)
    p.conn(o, 1, rt, 0)
    p.conn(o, 0, mul, 0)
    p.conn(mul, 0, dac, 0)
    p.conn(mul, 0, dac, 1)
    p.conn(o, 1, pr, 0)

    # --- text sections ---
    for title, lines, sy in placed:
        p.heading(CX, sy, title, 14)
        p.comment(TX, sy + 24, lines)
    p.comment(TX, credits_y, ["Credits: mdkit by soejrd (CC0)",
                              "Pd wrapper skandrums-pd (CC0), built with Claude (Anthropic)",
                              "Machine texts: Elektron Machinedrum manual, Appendix A"])

    head = f"#N canvas 348 20 {YEL_X + YEL_W + 2 * M + 20} {bar_bottom + M} 12;"
    return head + "\n" + "\n".join(p.lines) + "\n" + "\n".join(p.conns) + "\n"


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    only = set(sys.argv[3:])
    os.makedirs(outdir, exist_ok=True)
    count = 0
    for line in open(src):
        name, _id, cnt, _sb, ctl = line.strip().split("|")
        fam, code = name.lower().split("-")
        short = fam + code
        if only and short not in only:
            continue
        ctls = [(c.split("=")[0], int(c.split("=")[1])) for c in ctl.split(",")]
        with open(os.path.join(outdir, short + "~-help.pd"), "w") as f:
            f.write(build(name, fam, code, ctls))
        count += 1
    print(f"{count} help patches in {outdir}")


if __name__ == "__main__":
    main()
