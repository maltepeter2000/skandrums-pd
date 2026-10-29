/* SPDX-License-Identifier: CC0-1.0
 * skcore: host-independent wrapper around one mdkit voice.
 * Adds host-rate conversion, velocity/level, choke, dump and
 * "done" detection. No Pd dependency, so it can be tested in plain C.
 */
#ifndef SKCORE_H
#define SKCORE_H
#include "mdkit.h"
#include "skres.h"

#define SK_DONE_DB_LINEAR 1.0e-4f   /* about -80 dB */
#define SK_DONE_QUIET_MS  50.0
#define SK_CHOKE_MS_DEFAULT 3.0

typedef struct skcore {
    const mdkit_voice *v;
    void *state;
    unsigned nctl;
    unsigned char ctl[MDKIT_MAX_CONTROLS];
    float level, vel;
    float gain, gstep;            /* choke ramp gain (1 = open) */
    double choke_ms;
    double host_sr;
    skres rs;
    int active, done_pending;
    unsigned quiet, quiet_need, idle, idle_max;
    int armed;
    float transpose;              /* semitones, applied by note */
} skcore;

/* returns 0 on success, -1 on allocation failure */
int  skcore_init(skcore *c, const mdkit_voice *v, double host_sr);
void skcore_free(skcore *c);
void skcore_set_samplerate(skcore *c, double host_sr);
void skcore_reset(skcore *c);                       /* re-init voice, defaults */
void skcore_set_control(skcore *c, unsigned i, int value);   /* clamps 0..127 */
int  skcore_find_control(const skcore *c, const char *name); /* case-insens., -1 */
void skcore_trigger(skcore *c, int velocity);
/* note-to-PTCH: sets PTCH from the measured table (ends clamped) and triggers.
 * Returns 1 when the voice has a table, else 0 (then only triggers). */
int  skcore_note(skcore *c, double note, int velocity);       /* velocity 1..127, 0 -> 127 */
void skcore_choke(skcore *c);
void skcore_defaults(skcore *c);
unsigned char skcore_default_of(const mdkit_voice *v, unsigned i);
void skcore_process(skcore *c, float *out, int frames);
int  skcore_take_done(skcore *c);                   /* 1 once after voice died */

#endif
