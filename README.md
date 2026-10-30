# skandrums-pd

Pure Data externals for the 30 drum voices of [mdkit](https://github.com/soejrd/mdkit):
one object per voice, for example `[trxb2~]`, `[trxch~]`, `[efmbd~]`, `[pisd~]`.
All objects are built from the same source file (`src/skdrums_tilde.c`); only the voice changes.
License: CC0 1.0, same as mdkit.

**Status**

| Platform | State |
| --- | --- |
| Linux (desktop) | builds, `make test` passes (30 voices, 924 checks) |
| macOS | builds as a universal binary (arm64 + x86_64) |
| Windows (PC) | builds with MinGW-w64 (cross-compiled and linked, setup function exported); not yet run on a Windows PC |
| Bela Pepper | built on the board, loads in Pd 0.55-2, plays (image v0.3.8h, block size 32) |


## Objects

| Object | Controls (default) |
| --- | --- |
| `trxb2~` | PTCH 60, DEC 65, RAMP 41, HOLD 62, TICK 91, NOIS 44, DIRT 26, DIST 16 |
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

Controls are integers 0-127. The names are the control names from mdkit; mdkit does not describe
what they do.

## Connections

| Connection | Type | Purpose |
| --- | --- | --- |
| Inlet | messages | all commands below |
| Outlet 0 | signal | mono audio |
| Outlet 1 | messages | events: `choke`, `done`, `value`, `dump` |

## Messages at the inlet

| Message | Effect |
| --- | --- |
| `bang` | trigger at full velocity |
| `<number>` | trigger with velocity 1-127 (0 is ignored) |
| `<control> <0..127>` | set a control by name, e.g. `ptch 64`, `dirt 90` |
| `ctl <index> <value>` | set a control by number (0-based, in the order of the table) |
| `params a b c ...` | set several controls starting at index 0 |
| `defaults` | set all controls to the voice defaults |
| `level <0..8>` | output level as a factor (default 1.0) |
| `reset` | restart the voice and set the controls to their defaults |
| `get <control>` | sends `value <control> <value>` to outlet 1 |
| `print` | voice, controls and sample rate to the Pd console |
| `choke` | fade the voice out within `chokems` (see Choke) |
| `chokems <ms>` | length of the fade, default 3 ms |
| `dump` | sends all controls as `dump <name> v0 v1 ...` to outlet 1 |
| `dump <name> v0 v1 ...` | restore the controls from an earlier dump |

## Choke (e.g. closed hat cuts off open hat)

Outlet 1 sends the message `choke` on every trigger. Connect it to the inlet of the voice that
should be cut off:

    [trxch~] outlet 1  ->  inlet [trxoh~]

On `choke`, `trxoh~` fades out within `chokems` (3 ms) and stays silent until it is triggered itself.
Every voice can choke any other voice, also several at once. The choke takes effect from the next
audio block.

## Presets and steps: `[skpreset]`

`dump` returns the current state as a message, `dump <name> v0 v1 ...` restores it.
The name after `dump` is the object name; a message with a different name is ignored.

The abstraction `pd/skpreset.pd` builds on this (help: `skpreset-help.pd`). It keeps 16 slots per
voice (for example one per step) in a `[text define -k name]` in the main patch, which is saved with
the patch:

    [trxb2~] outlet 1  ->  [skpreset name] inlet 0
    [skpreset name] outlet 0  ->  inlet [trxb2~]
    [hradio] (0..15)   ->  [skpreset name] inlet 1

When the slot changes, the current values are first written to the old slot, then the new slot is
loaded. An empty slot takes over the current sound. Outlet 1 of `[skpreset]` sends the loaded values
as a list (for number boxes). For several voices use one text and one `[skpreset]` per voice, with
all slot inlets driven from one `[hradio]`.

`done` arrives at outlet 1 when the voice stays below about -80 dB for longer than 50 ms.

## Sample rate

The voices run internally at 44,100 Hz. If Pd runs at 44,100 Hz the signal passes unchanged
(bit-identical with mdkit). At other rates it is converted with a Kaiser-sinc resampler (64 taps).

## Building

Requirements: a C compiler, `make` and the Pd headers (`m_pd.h`).
Only some voices: `make VOICES="trx/b2 trx/ch trx/oh"`.

### Desktop: macOS

Pd vanilla in `/Applications` (the headers are taken from the app bundle):

    make            # all 30, universal arm64 + x86_64 -> out/*.pd_darwin
    make install    # copies to ~/Documents/Pd/externals

Restart Pd afterwards. If the headers are not found, pass `PDINC=/path/to/dir/with/m_pd.h`.

### Desktop: Linux

    make PDINC=/usr/include/pd     # -> out/*.pd_linux
    make install                   # copies to ~/pd-externals

Add `~/pd-externals` to the Pd search path (Preferences > Path) and restart Pd.

### Desktop: Windows (PC)

64-bit Pd vanilla for Windows and the MinGW-w64 toolchain from MSYS2. The build was checked with a
MinGW-w64 cross compiler; it has not yet been run on a real Windows PC, so please report problems.

1. Install [Pd vanilla](https://puredata.info/downloads/pure-data) (64-bit installer) and
   [MSYS2](https://www.msys2.org).
2. Open the **MSYS2 MinGW x64** shell (not the plain "MSYS2 MSYS" one) and install the tools:

        pacman -S --needed make mingw-w64-x86_64-gcc

3. Go to the source folder (unzip the repository, then `cd /c/Users/<you>/Downloads/skandrums-pd-main`)
   and build:

        make PDDIR="C:/Program Files/Pd"     # -> out/*.dll

   `PDDIR` is the Pd installation folder; it must contain `src/m_pd.h` and `bin/pd.dll`. Change it
   if Pd is installed elsewhere. Alternatively pass `PDINC=` (header folder) and `PDBIN=` (folder
   with `pd.dll`) separately.
4. Install:

        make install                         # copies to %APPDATA%\Pd

   Pd searches `%APPDATA%\Pd` by default; otherwise add the folder under File > Preferences > Path.
   Restart Pd afterwards.

`make test` also works in this shell.

### Bela (tested on the Bela Pepper)

The externals are built on the board itself, so no cross compiler is needed. Pd on the Bela image
is Pd 0.55-2; the Pd headers are in `/usr/local/include/libpd/`.

1. Copy the sources to the board (from the computer; `bela.local` is the board's address):

        rsync -av --exclude '.git' --exclude 'out' ./ root@bela.local:/root/skandrums-pd/

2. Build on the board (a few minutes; `tail` prints only when the build is finished):

        ssh root@bela.local
        cd /root/skandrums-pd
        make -j2 PDINC=/usr/local/include/libpd/
        ls out/*.pd_linux | wc -l          # should print 30

3. Copy the externals **flat** into the Bela externals folder (no subfolder; a `[declare -path]`
   to a subfolder is not picked up on the board):

        cp out/*.pd_linux pd/skpreset.pd /root/Bela/projects/pd-externals/

4. Use the objects in a Bela Pd project exactly like on the desktop (`[trxb2~]`, no `declare`
   needed). Restart the project; the Pd console must not show `couldn't create`.

Notes for the Bela: set the block size to 32 for low latency (`-p 32`); the voices render only while
they are active, so idle voices cost almost nothing.

## Tests

    make test       # all 30 voices, without Pd
    make bench BS=32   # relative CPU cost per voice at a given block size

Per voice the tests check: bit-identical output at 44.1 kHz, identical output for different block
sizes (also at 48 kHz), linear velocity, choke (silence after 3 ms, no click, retrigger), controls,
presets and `done`. In addition `tests/pd/gen_events.py` generates a Pd run with
`trxch~` -> `trxoh~`.

## Help patches

`make help` regenerates `help/*.pd` and `pd/skpreset.pd` (needs `python3`).

## Origin

`mdkit/` is an unmodified copy of soejrd/mdkit (commit in `mdkit/COMMIT`, CC0).
`src/` is the Pd wrapper of this project. The resampler `src/skres.c` comes from the earlier
digidrum externals.
