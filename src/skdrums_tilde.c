/* SPDX-License-Identifier: CC0-1.0
 * skandrums-pd: one Pure Data object per mdkit voice.
 *
 * This file is compiled once per voice; the Makefile selects the voice with
 *   -DSK_OBJ_NAME="trxb2~"  -DSK_SHORT="trxb2"  -DSK_SETUP=trxb2_tilde_setup
 *   -DSK_VOICE=mdkit_voice_trx_b2  -DSK_HEADER="mdkit_trx_b2.h"
 *
 * Inlet 0   : messages (see README)
 * Outlet 0  : signal
 * Outlet 1  : events: choke, done, value <name> <v>, dump <short> <v...>
 */
#include <stdio.h>
#include <string.h>
#include "m_pd.h"
#include SK_HEADER
#include "skcore.h"

#if defined(__GNUC__)
#define SK_EXPORT __attribute__((visibility("default")))
#else
#define SK_EXPORT
#endif

static t_class *sk_class;

typedef struct _sk {
    t_object  x_obj;
    skcore    c;
    int       ok;
    t_outlet *o_sig, *o_ev;
    t_clock  *clk;
} t_sk;

static int iround(t_float f) { return (int)(f >= 0 ? f + 0.5f : f - 0.5f); }

/* ---- DSP ---- */
static t_int *sk_perform(t_int *w)
{
    t_sk *x = (t_sk *)(w[1]);
    t_sample *out = (t_sample *)(w[2]);
    int n = (int)(w[3]);
    float tmp[64];
    if (!x->ok) { while (n--) *out++ = 0; return w + 4; }
    while (n > 0) {
        int b = n > 64 ? 64 : n, i;
        skcore_process(&x->c, tmp, b);
        for (i = 0; i < b; ++i) out[i] = (t_sample)tmp[i];
        out += b;
        n -= b;
    }
    if (skcore_take_done(&x->c)) clock_delay(x->clk, 0);
    return w + 4;
}

static void sk_dsp(t_sk *x, t_signal **sp)
{
    if (x->ok) skcore_set_samplerate(&x->c, sp[0]->s_sr);
    dsp_add(sk_perform, 3, x, sp[0]->s_vec, (t_int)sp[0]->s_n);
}

static void sk_done_tick(t_sk *x)
{
    outlet_anything(x->o_ev, gensym("done"), 0, NULL);
}

/* ---- helpers ---- */
static void emit_values(t_sk *x, const char *sel, const unsigned char *v)
{
    t_atom a[1 + MDKIT_MAX_CONTROLS];
    unsigned i;
    SETSYMBOL(a, gensym(SK_SHORT));
    for (i = 0; i < x->c.nctl; ++i) SETFLOAT(a + 1 + i, v[i]);
    outlet_anything(x->o_ev, gensym(sel), (int)x->c.nctl + 1, a);
}

static void do_trigger(t_sk *x, int vel)
{
    if (!x->ok) return;
    skcore_trigger(&x->c, vel);
    outlet_anything(x->o_ev, gensym("choke"), 0, NULL);   /* tell the choke targets */
}

/* ---- messages ---- */
static void sk_bang(t_sk *x) { do_trigger(x, 127); }

static void sk_float(t_sk *x, t_floatarg f)
{
    int v = iround(f);
    if (v <= 0) return;
    if (v > 127) v = 127;
    do_trigger(x, v);
}

static void sk_anything(t_sk *x, t_symbol *s, int argc, t_atom *argv)
{
    const char *m = s->s_name;
    int i;
    if (!x->ok) return;

    /* control by name: "ptch 64" */
    i = skcore_find_control(&x->c, m);
    if (i >= 0) {
        if (argc >= 1 && argv[0].a_type == A_FLOAT)
            skcore_set_control(&x->c, (unsigned)i, iround(atom_getfloat(argv)));
        else pd_error(x, SK_OBJ_NAME ": '%s' needs a number 0..127", m);
        return;
    }
    if (!strcmp(m, "ctl")) {
        if (argc >= 2 && argv[0].a_type == A_FLOAT && argv[1].a_type == A_FLOAT) {
            int k = iround(atom_getfloat(argv));
            if (k < 0 || k >= (int)x->c.nctl)
                pd_error(x, SK_OBJ_NAME ": ctl index must be 0..%d", (int)x->c.nctl - 1);
            else skcore_set_control(&x->c, (unsigned)k, iround(atom_getfloat(argv + 1)));
        } else pd_error(x, SK_OBJ_NAME ": usage: ctl <index> <value>");
    } else if (!strcmp(m, "params")) {
        for (i = 0; i < argc && i < (int)x->c.nctl; ++i)
            if (argv[i].a_type == A_FLOAT)
                skcore_set_control(&x->c, (unsigned)i, iround(atom_getfloat(argv + i)));
    } else if (!strcmp(m, "dump")) {
        if (argc == 0) {
            emit_values(x, "dump", x->c.ctl);
        } else if (argv[0].a_type == A_SYMBOL &&
                   !strcmp(atom_getsymbol(argv)->s_name, SK_SHORT)) {
            for (i = 1; i < argc && i <= (int)x->c.nctl; ++i)   /* restore */
                if (argv[i].a_type == A_FLOAT)
                    skcore_set_control(&x->c, (unsigned)(i - 1), iround(atom_getfloat(argv + i)));
        }
        /* a dump from another voice type is ignored on purpose */
    } else if (!strcmp(m, "get")) {
        if (argc >= 1 && argv[0].a_type == A_SYMBOL) {
            const char *nm = atom_getsymbol(argv)->s_name;
            int k = skcore_find_control(&x->c, nm);
            if (k < 0) pd_error(x, SK_OBJ_NAME ": no control '%s'", nm);
            else {
                t_atom a[2];
                SETSYMBOL(a, atom_getsymbol(argv));
                SETFLOAT(a + 1, x->c.ctl[k]);
                outlet_anything(x->o_ev, gensym("value"), 2, a);
            }
        }
    } else if (!strcmp(m, "note")) {
        /* note <midinote> [velocity]: PTCH from the measured table (if any), then trigger */
        if (argc >= 1 && argv[0].a_type == A_FLOAT) {
            int vel = argc >= 2 ? iround(atom_getfloat(argv + 1)) : 127;
            if (vel <= 0) return;           /* note-off */
            if (vel > 127) vel = 127;
            if (x->ok) {
                skcore_note(&x->c, atom_getfloat(argv), vel);
                outlet_anything(x->o_ev, gensym("choke"), 0, NULL);
            }
        } else pd_error(x, SK_OBJ_NAME ": usage: note <midinote> [velocity]");
    } else if (!strcmp(m, "transpose")) {
        x->c.transpose = argc >= 1 ? atom_getfloat(argv) : 0;
    } else if (!strcmp(m, "defaults")) {
        skcore_defaults(&x->c);
    } else if (!strcmp(m, "level")) {
        t_float f = argc >= 1 ? atom_getfloat(argv) : 1;
        x->c.level = f < 0 ? 0 : (f > 8 ? 8 : f);
    } else if (!strcmp(m, "choke")) {
        skcore_choke(&x->c);
    } else if (!strcmp(m, "chokems")) {
        t_float f = argc >= 1 ? atom_getfloat(argv) : SK_CHOKE_MS_DEFAULT;
        x->c.choke_ms = f < 0 ? 0 : (f > 2000 ? 2000 : f);
    } else if (!strcmp(m, "reset")) {
        skcore_reset(&x->c);
    } else if (!strcmp(m, "print")) {
        unsigned k;
        post(SK_OBJ_NAME ": %s, host %.0f Hz, core %.0f Hz (%s), level %.2f, choke %.1f ms",
             x->c.v->name, x->c.host_sr, SKRES_NATIVE_RATE,
             x->c.rs.bypass ? "direct" : "resampled", x->c.level, x->c.choke_ms);
        for (k = 0; k < x->c.nctl; ++k)
            post("  %u %-5s %3d", k, x->c.v->control_names[k], x->c.ctl[k]);
    } else if (!strcmp(m, "done") || !strcmp(m, "value")) {
        /* events from another voice's outlet 1: ignored so it can be wired directly */
    } else {
        pd_error(x, SK_OBJ_NAME ": no method for '%s'", m);
    }
}

/* ---- life cycle ---- */
static void *sk_new(void)
{
    t_sk *x = (t_sk *)pd_new(sk_class);
    x->o_sig = outlet_new(&x->x_obj, &s_signal);
    x->o_ev  = outlet_new(&x->x_obj, 0);
    x->clk   = clock_new(x, (t_method)sk_done_tick);
    x->ok = (skcore_init(&x->c, &SK_VOICE, sys_getsr()) == 0);
    if (!x->ok) pd_error(x, SK_OBJ_NAME ": out of memory");
    return x;
}

static void sk_free(t_sk *x)
{
    clock_free(x->clk);
    if (x->ok) skcore_free(&x->c);
}

SK_EXPORT void SK_SETUP(void)
{
    sk_class = class_new(gensym(SK_OBJ_NAME), (t_newmethod)sk_new, (t_method)sk_free,
                         sizeof(t_sk), CLASS_DEFAULT, 0);
    class_addmethod(sk_class, (t_method)sk_dsp, gensym("dsp"), A_CANT, 0);
    class_addbang(sk_class, sk_bang);
    class_addfloat(sk_class, sk_float);
    class_addanything(sk_class, sk_anything);
}
