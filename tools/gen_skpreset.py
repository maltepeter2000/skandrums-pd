#!/usr/bin/env python3
"""Generate pd/skpreset.pd (the step/preset abstraction)."""
import sys
B = chr(92)
objs = [  # (index comment, text)
 ("A inlet: voice outlet 1", "#X obj 20 20 inlet"),                 # 0
 ("B inlet: slot 0-15", "#X obj 300 20 inlet"),                     # 1
 ("out 0 -> voice inlet", "#X obj 20 560 outlet"),                  # 2
 ("out 1 -> values", "#X obj 400 560 outlet"),                      # 3
 ("", "#X obj 20 60 route dump"),                                   # 4
 ("", "#X obj 20 90 list prepend"),                                 # 5
 ("", f"#X obj 20 120 text set {B}$1"),                             # 6
 ("", "#X obj 300 50 i"),                                           # 7
 ("", "#X obj 300 80 clip 0 15"),                                   # 8
 ("", "#X obj 300 110 t f f b"),                                    # 9
 ("", "#X msg 380 150 dump"),                                       # 10 commit
 ("", f"#X obj 300 190 text get {B}$1"),                            # 11
 ("", "#X obj 300 220 t l l"),                                      # 12
 ("", "#X obj 400 250 list length"),                                # 13
 ("", "#X obj 400 280 moses 2"),                                    # 14
 ("", "#X obj 400 310 t f f"),                                      # 15
 ("", "#X msg 460 340 0"),                                          # 16
 ("", "#X msg 520 310 1"),                                          # 17
 ("", "#X obj 300 370 spigot"),                                     # 18
 ("", "#X msg 400 340 dump"),                                       # 19 empty -> take current state
 ("", "#X obj 300 400 t l l"),                                      # 20
 ("", "#X obj 300 430 list prepend dump"),                          # 21
 ("", "#X obj 300 460 list trim"),                                  # 22
 ("", "#X obj 400 430 list split 1"),                               # 23
 ("", "#X obj 600 20 loadbang"),                                    # 24
 ("", f"#X obj 600 50 text size {B}$1"),                            # 25
 ("", "#X obj 600 80 moses 16"),                                    # 26
 ("", "#X obj 600 110 - 16"),                                       # 27
 ("", "#X obj 600 140 * -1"),                                       # 28
 ("", "#X obj 600 170 until"),                                      # 29
 ("", "#X obj 600 200 t b b"),                                      # 30
 ("", f"#X obj 640 230 text size {B}$1"),                           # 31
 ("", "#X msg 600 230 list -"),                                     # 32
 ("", f"#X obj 600 270 text set {B}$1"),                            # 33
]
conns = [
 (0,0,4,0),(4,0,5,0),(5,0,6,0),
 (1,0,7,0),(7,0,8,0),(8,0,9,0),
 (9,2,10,0),(10,0,2,0),            # 1. commit: ask the voice for its values
 (9,1,6,1),                        # 2. current line := N
 (9,0,11,0),                       # 3. load line N
 (11,0,12,0),(12,1,13,0),(13,0,14,0),
 (14,0,15,0),(14,1,17,0),(17,0,18,1),
 (15,1,16,0),(16,0,18,1),(15,0,19,0),(19,0,2,0),
 (12,0,18,0),(18,0,20,0),
 (20,1,21,0),(21,0,22,0),(22,0,2,0),
 (20,0,23,0),(23,1,3,0),
 (24,0,25,0),(25,0,26,0),(26,0,27,0),(27,0,28,0),(28,0,29,0),(29,0,30,0),
 (30,1,31,0),(31,0,33,1),(30,0,32,0),(32,0,33,0),
]
txt = ["#N canvas 0 50 760 620 12;"]
txt += [o + ";" for _, o in objs]
txt += [f"#X connect {a} {b} {c} {d};" for a, b, c, d in conns]
open(sys.argv[1], "w").write("\n".join(txt) + "\n")
