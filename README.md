# skandrums-pd

Pure-Data-Objekte für die 30 Drum-Stimmen aus [mdkit](https://github.com/soejrd/mdkit):
je Stimme ein eigenes Objekt, zum Beispiel `[trxb2~]`, `[trxch~]`, `[efmbd~]`, `[pisd~]`.
Alle Objekte entstehen aus demselben Quelltext (`src/skdrums_tilde.c`), nur die Stimme wechselt.
Lizenz: CC0 1.0, wie mdkit.

**Stand:** Auf Linux gebaut und getestet (siehe unten). macOS und Bela sind noch nicht getestet.
Help-Patches fehlen noch.

## Objekte

| Objekt | Controls (Default) |
| --- | --- |
| `trxb2~` | PTCH 60, DEC 65, RAMP 41, HOLD 62, TICK 91, NOIS 44, DIRT 56, DIST 58 |
| `trxbd~` | PTCH 64, DEC 64, RAMP 0, RDEC 0, STRT 0, NOIS 0, HARM 0, CLIP 0 |
| `trxcb~` | PTCH 100, DEC 50, ENH 127, DAMP 127, TONE 0, BUMP 0 |
| `trxch~` | GAP 0, DEC 8, HPF 0, LPF 127, MTAL 0 |
| `trxcl~` | PTCH 64, DEC 32, DUAL 64, ENH 0, TUNE 64, CLIC 0 |
| `trxcp~` | CLPY 50, TONE 100, HARD 7, RICH 127, RATE 40, ROOM 64, RSIZ 0, RTUN 90 |
| `trxcy~` | RICH 127, DEC 0, TOP 0, TTUN 127, SIZE 0, PEAK 127 |
| `trxma~` | ATT 32, SUS 32, REV 0, DAMP 0, RATL 64, RTYP 64, TONE 64, HARD 64 |
| `trxoh~` | GAP 50, DEC 60, HPF 8, LPF 127, MTAL 0 |
| `trxrs~` | PTCH 50, DEC 0, DIST 50 |
| `trxsd~` | PTCH 35, DEC 7, BUMP 0, BENV 64, SNAP 127, TONE 0, TUNE 100, CLIP 90 |
| `trxxc~` | PTCH 64, DEC 32, RAMP 32, RDEC 100, DAMP 0, DIST 0, DTYP 0 |
| `trxxt~` | PTCH 70, DEC 25, RAMP 50, RDEC 30, DAMP 64, DIST 32, DTYP 0 |
| `efmbd~` | PTCH 0, DEC 64, RAMP 32, RDEC 127, MOD 35, MFRQ 14, MDEC 64, MFB 24 |
| `efmcb~` | PTCH 54, DEC 61, SNAP 92, FB 56, MOD 17, MFRQ 112, MDEC 42 |
| `efmcp~` | PTCH 50, DEC 40, CLPS 127, CDEC 24, MOD 115, MFRQ 36, MDEC 87, HPF 8 |
| `efmcy~` | PTCH 64, DEC 72, FB 96, HPF 92, MOD 45, MFRQ 32, MDEC 64 |
| `efmhh~` | PTCH 26, DEC 54, TREM 26, TFRQ 47, MOD 0, MFRQ 86, MDEC 93, FB 75 |
| `efmrs~` | PTCH 67, DEC 10, MOD 8, HPF 15, SNAR 38, SPTC 25, SDEC 59, SMOD 0 |
| `efmsd~` | PTCH 27, DEC 60, NOIS 14, NDEC 79, MOD 0, MFRQ 5, MDEC 127, HPF 29 |
| `efmxt~` | PTCH 25, DEC 50, RAMP 127, RDEC 111, MOD 5, MFRQ 4, MDEC 79, CLIC 0 |
| `pibd~` | PTCH 64, DEC 35, HARD 100, HAMR 0, TENS 127, DAMP 100 |
| `picc~` | PTCH 64, DEC 70, HARD 90, RING 32, AG 127, AU 127, BR 64, GRAB 127 |
| `pihh~` | PTCH 64, DEC 70, CLSN 100, RING 30, AG 127, AU 127, BR 60, CLOS 127 |
| `pima~` | GRNS 90, DEC 0, GLEN 72, SIZE 96, HARD 64 |
| `piml~` | PTCH 0, DEC 64, HARD 127, TENS 0 |
| `pimt~` | PTCH 20, DEC 20, HARD 127, HAMR 127, TUNE 127, DAMP 80, SIZE 90, POS 64 |
| `pirc~` | PTCH 64, DEC 70, HARD 96, RING 32, AG 127, AU 127, BR 64, GRAB 127 |
| `pirs~` | PTCH 90, DEC 48, HARD 64, RING 64, RVOL 64, RDEC 64 |
| `pisd~` | PTCH 64, DEC 64, HARD 10, RING 40, TENS 90, RVOL 80, RDEC 80 |

Controls sind ganze Zahlen 0–127. Die Namen sind die Control-Namen aus mdkit; welche Wirkung sie
haben, steht in mdkit nicht beschrieben.

## Anschlüsse

| Anschluss | Typ | Aufgabe |
| --- | --- | --- |
| Inlet | Messages | alle Befehle unten |
| Outlet 0 | Signal | Mono-Audio |
| Outlet 1 | Messages | Ereignisse: `choke`, `done`, `value`, `dump` |

## Messages am Inlet

| Message | Wirkung |
| --- | --- |
| `bang` | Trigger mit voller Stärke |
| `<zahl>` | Trigger mit Anschlagstärke 1–127 (0 wird ignoriert) |
| `<control> <0..127>` | Control per Namen setzen, z. B. `ptch 64`, `dirt 90` |
| `ctl <index> <wert>` | Control per Nummer (0-basiert, Reihenfolge der Tabelle) |
| `params a b c ...` | mehrere Controls ab Index 0 setzen |
| `defaults` | alle Controls auf die Defaults der Stimme |
| `level <0..8>` | Ausgangspegel als Faktor (Default 1.0) |
| `reset` | Stimme neu starten, Controls auf Default |
| `get <control>` | sendet `value <control> <wert>` an Outlet 1 |
| `print` | Stimme, Controls und Samplerate in die Pd-Konsole |
| `choke` | Stimme in `chokems` ausblenden (siehe Choke) |
| `chokems <ms>` | Länge der Ausblendung, Default 3 ms |
| `store <0..15>` | aktuelle Controls in Speicherplatz legen |
| `recall <0..15>` | Speicherplatz laden |
| `dump` | alle Controls als `dump <name> v0 v1 ...` an Outlet 1 |
| `dump <0..15>` | Inhalt eines Speicherplatzes ausgeben |
| `dump <name> v0 v1 ...` | Controls aus einem früheren Dump zurückladen |

## Choke (z. B. Closed Hat schneidet Open Hat ab)

Outlet 1 sendet bei jedem Trigger die Message `choke`. Verbinde ihn mit dem Inlet der Stimme,
die verstummen soll:

    [trxch~] Outlet 1  ->  Inlet [trxoh~]

`trxoh~` blendet auf `choke` in `chokems` (3 ms) aus und bleibt still, bis es selbst getriggert wird.
Jede Stimme kann jede andere choken, auch mehrere. Der Choke wirkt ab dem nächsten Audioblock.

## Presets

`dump` liefert den aktuellen Zustand als Message, die du in `[text]`, `[coll]` oder einer
Datei ablegen kannst. Dieselbe Message ruft ihn wieder auf, zum Beispiel für `[trxb2~]`:

    dump trxb2 60 65 41 62 91 44 56 58

Der Name nach `dump` ist der Objektname. Eine Message mit fremdem Namen wird ignoriert, so kann
Outlet 1 gefahrlos an eine andere Stimme gehen. Zusätzlich gibt es 16 interne Speicherplätze
(`store`/`recall`), die nicht gespeichert werden und beim Schließen des Patches verloren gehen.

`done` kommt an Outlet 1, wenn die Stimme länger als 50 ms unter etwa −80 dB bleibt.

## Samplerate

Die Stimmen laufen intern mit 44 100 Hz. Läuft Pd mit 44 100 Hz, geht das Signal unverändert durch
(bit-gleich mit mdkit). Bei anderen Raten wird mit einem Kaiser-Sinc-Resampler (64 Taps) umgerechnet.

## Bauen

Voraussetzung: C-Compiler, `make` und die Pd-Header (`m_pd.h`).

macOS (Pd vanilla in /Applications):

    make            # alle 30, universal arm64 + x86_64
    make install    # nach ~/Documents/Pd/externals

Pd danach neu starten.

Linux / Bela:

    make PDINC=/usr/include/pd          # bei Bela ggf. /usr/local/include/libpd
    make install                        # nach ~/pd-externals

Nur einige Stimmen: `make VOICES="trx/b2 trx/ch trx/oh"`.

## Tests

    make test       # alle 30 Stimmen, ohne Pd

Geprüft wird je Stimme: bit-gleiche Ausgabe bei 44,1 kHz, gleiche Ausgabe bei verschiedenen
Blockgrößen (auch bei 48 kHz), lineare Anschlagstärke, Choke (Stille nach 3 ms, kein Knacken,
Retrigger), Controls, Presets und `done`. Dazu erzeugt `tests/pd/gen_events.py` einen Pd-Lauf mit
`trxch~` → `trxoh~`.

## Herkunft

`mdkit/` ist eine unveränderte Kopie von soejrd/mdkit (Commit in `mdkit/COMMIT`, CC0).
`src/` ist der Pd-Wrapper dieses Projekts. Der Resampler `src/skres.c` stammt aus den früheren
digidrum-Externals.
