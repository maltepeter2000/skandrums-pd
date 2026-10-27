/* SPDX-License-Identifier: CC0-1.0 */
#include <ctype.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "skcore.h"

static unsigned char default_of(const skcore *c, unsigned i)
{
    return c->v->control_defaults ? c->v->control_defaults[i] : 64;
}

static void apply_all(skcore *c)
{
    unsigned i;
    for (i = 0; i < c->nctl; ++i) c->v->set_control(c->state, i, c->ctl[i]);
}

static void rate_changed(skcore *c)
{
    c->quiet_need = (unsigned)(SK_DONE_QUIET_MS * 0.001 * c->host_sr + 0.5);
    if (c->quiet_need < 1) c->quiet_need = 1;
    c->idle_max = (unsigned)(2.0 * c->host_sr);
}

int skcore_init(skcore *c, const mdkit_voice *v, double host_sr)
{
    unsigned i;
    memset(c, 0, sizeof *c);
    c->v = v;
    c->state = calloc(1, v->state_bytes ? v->state_bytes : 1);
    if (!c->state) return -1;
    c->nctl = v->control_count > MDKIT_MAX_CONTROLS ? MDKIT_MAX_CONTROLS : v->control_count;
    v->init(c->state);
    for (i = 0; i < c->nctl; ++i) c->ctl[i] = default_of(c, i);
    c->level = 1.f; c->vel = 1.f; c->gain = 1.f; c->gstep = 0.f;
    c->choke_ms = SK_CHOKE_MS_DEFAULT;
    c->host_sr = host_sr > 0 ? host_sr : SKRES_NATIVE_RATE;
    skres_init(&c->rs, c->host_sr);
    rate_changed(c);
    return 0;
}

void skcore_free(skcore *c)
{
    free(c->state);
    c->state = NULL;
}

void skcore_set_samplerate(skcore *c, double host_sr)
{
    if (host_sr <= 0) return;
    c->host_sr = host_sr;
    skres_set_samplerate(&c->rs, host_sr);
    rate_changed(c);
}

void skcore_reset(skcore *c)
{
    unsigned i;
    c->v->init(c->state);
    for (i = 0; i < c->nctl; ++i) c->ctl[i] = default_of(c, i);
    skres_reset(&c->rs);
    c->gain = 1.f; c->gstep = 0.f; c->active = 0; c->done_pending = 0; c->quiet = 0;
}

void skcore_defaults(skcore *c)
{
    unsigned i;
    for (i = 0; i < c->nctl; ++i) c->ctl[i] = default_of(c, i);
    apply_all(c);
}

void skcore_set_control(skcore *c, unsigned i, int value)
{
    if (i >= c->nctl) return;
    if (value < 0) value = 0;
    if (value > 127) value = 127;
    c->ctl[i] = (unsigned char)value;
    c->v->set_control(c->state, i, (unsigned)value);
}

int skcore_find_control(const skcore *c, const char *name)
{
    unsigned i;
    for (i = 0; i < c->nctl; ++i) {
        const char *a = c->v->control_names[i], *b = name;
        while (*a && *b && tolower((unsigned char)*a) == tolower((unsigned char)*b)) { ++a; ++b; }
        if (!*a && !*b) return (int)i;
    }
    return -1;
}

void skcore_trigger(skcore *c, int velocity)
{
    if (velocity <= 0 || velocity > 127) velocity = 127;
    c->vel = (float)velocity / 127.f;
    c->gain = 1.f; c->gstep = 0.f;
    c->v->trigger(c->state);
    c->active = 1; c->quiet = 0; c->idle = 0; c->armed = 0; c->done_pending = 0;
}

void skcore_choke(skcore *c)
{
    double n = c->choke_ms * 0.001 * c->host_sr;
    if (!c->active) return;
    if (n < 1.0) { c->gain = 0.f; c->gstep = 0.f; c->active = 0; return; }
    c->gstep = (float)(1.0 / n);
}

int skcore_store(skcore *c, unsigned slot)
{
    if (slot >= SK_SLOTS) return -1;
    memcpy(c->slot[slot], c->ctl, sizeof c->ctl);
    c->slot_used[slot] = 1;
    return 0;
}

int skcore_recall(skcore *c, unsigned slot)
{
    if (slot >= SK_SLOTS || !c->slot_used[slot]) return -1;
    memcpy(c->ctl, c->slot[slot], sizeof c->ctl);
    apply_all(c);
    return 0;
}

static void render_cb(void *ctx, float *dst, int frames)
{
    skcore *c = (skcore *)ctx;
    c->v->render(c->state, dst, (unsigned)frames);
}

void skcore_process(skcore *c, float *out, int frames)
{
    int i;
    skres_process(&c->rs, out, frames, render_cb, c);
    for (i = 0; i < frames; ++i) {
        float raw = out[i];
        out[i] = raw * (c->level * c->vel * c->gain);
        if (c->gstep > 0.f) {
            c->gain -= c->gstep;
            if (c->gain <= 0.f) { c->gain = 0.f; c->gstep = 0.f; c->active = 0; }
        }
        if (c->active) {
            if (fabsf(raw) >= SK_DONE_DB_LINEAR) {
                c->armed = 1; c->quiet = 0;
            } else if (c->armed && ++c->quiet >= c->quiet_need) {
                c->active = 0; c->done_pending = 1;
            } else if (!c->armed && ++c->idle >= c->idle_max) {
                c->active = 0;      /* never became audible: give up silently */
            }
        }
    }
}

int skcore_take_done(skcore *c)
{
    int d = c->done_pending;
    c->done_pending = 0;
    return d;
}
