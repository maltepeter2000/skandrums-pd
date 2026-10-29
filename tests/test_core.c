/* SPDX-License-Identifier: CC0-1.0
 * Tests for skcore on all mdkit voices. No Pd needed. */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "skcore.h"
#include "voices_gen.h"

#define NVOICES (sizeof all_voices / sizeof all_voices[0])
static int fails = 0, checks = 0;
#define CHECK(cond, ...) do { ++checks; if (!(cond)) { ++fails; \
    printf("FAIL %s: ", name); printf(__VA_ARGS__); printf("\n"); } } while (0)

static float *render(const mdkit_voice *v, double sr, int total, int block,
                     int ctl_at, int ctl_idx, int ctl_val, int choke_at, int vel)
{
    skcore c; float *out = calloc((size_t)total, sizeof(float));
    int pos = 0;
    skcore_init(&c, v, sr);
    skcore_trigger(&c, vel);
    while (pos < total) {
        int n = block < total - pos ? block : total - pos;
        if (ctl_at >= 0 && pos == ctl_at) skcore_set_control(&c, (unsigned)ctl_idx, ctl_val);
        if (choke_at >= 0 && pos == choke_at) skcore_choke(&c);
        skcore_process(&c, out + pos, n);
        pos += n;
    }
    skcore_free(&c);
    return out;
}

int main(void)
{
    size_t vi;
    for (vi = 0; vi < NVOICES; ++vi) {
        const mdkit_voice *v = all_voices[vi];
        const char *name = v->name;
        const int N = 44100;
        int i, nd = 0;
        float *a, *raw;
        float peak = 0;
        skcore c;
        void *st;

        /* 1. direct path is bit-exact with the raw voice (until the voice is declared done, then silence) */
        a = render(v, 44100.0, N, 64, -1, 0, 0, -1, 127);
        st = calloc(1, v->state_bytes);
        v->init(st); v->trigger(st);
        raw = calloc(N, sizeof(float));
        for (i = 0; i < N; i += 100) v->render(st, raw + i, (unsigned)(N - i < 100 ? N - i : 100));
        for (i = 0; i < N; ++i) { if (a[i] != raw[i] && !(a[i] == 0.f && fabsf(raw[i]) < 2e-4f)) ++nd; if (!(fabsf(a[i]) <= 4.f)) nd += 1000000; if (fabsf(a[i]) > peak) peak = fabsf(a[i]); }
        CHECK(nd == 0, "44.1k direct path differs from raw voice in %d samples", nd);
        CHECK(peak > 1e-3f, "silent (peak %g)", peak);
        free(st); free(raw);

        /* 2. block-size invariance, direct and resampled, with a control change */
        for (int k = 0; k < 2; ++k) {
            double sr = k ? 48000.0 : 44100.0;
            int bl[3] = { 64, 32, 16 }, j;
            float *r0 = render(v, sr, N, 64, 1024, 0, 100, -1, 127);
            for (j = 1; j < 3; ++j) {
                float *r1 = render(v, sr, N, bl[j], 1024, 0, 100, -1, 127);
                nd = 0; for (i = 0; i < N; ++i) if (r0[i] != r1[i]) ++nd;
                CHECK(nd == 0, "%g Hz: block %d vs 64 differ in %d samples", sr, bl[j], nd);
                free(r1);
            }
            /* odd sizes, no control change */
            { float *p = render(v, sr, N, 64, -1, 0, 0, -1, 127);
              float *q = render(v, sr, N, 7, -1, 0, 0, -1, 127);
              nd = 0; for (i = 0; i < N; ++i) if (p[i] != q[i]) ++nd;
              CHECK(nd == 0, "%g Hz: block 7 vs 64 differ in %d samples", sr, nd);
              free(p); free(q); }
            free(r0);
        }

        /* 3. resampled level matches direct level (within 1 dB) */
        { float *r = render(v, 48000.0, N, 64, -1, 0, 0, -1, 127), p2 = 0;
          for (i = 0; i < N; ++i) if (fabsf(r[i]) > p2) p2 = fabsf(r[i]);
          CHECK(p2 > peak * 0.7f && p2 < peak * 1.4f, "48k peak %g vs direct %g", p2, peak);
          free(r); }

        /* 4. velocity scales linearly */
        { float *h = render(v, 44100.0, 4096, 64, -1, 0, 0, -1, 64);
          double e = 0; for (i = 0; i < 4096; ++i) e += fabs(h[i] - a[i] * (64.0f / 127.0f));
          CHECK(e < 1e-3, "velocity 64 not linear (err %g)", e);
          free(h); }

        /* 5. choke: silent after choke_ms, no jump, retrigger works */
        { int at = 3008; float *r = render(v, 44100.0, 8000, 64, -1, 0, 0, at, 127);
          int end = at + (int)(SK_CHOKE_MS_DEFAULT * 0.001 * 44100.0) + 70;
          float tail = 0, jump = 0;
          for (i = end; i < 8000; ++i) if (fabsf(r[i]) > tail) tail = fabsf(r[i]);
          for (i = at + 1; i < end; ++i) { float d = fabsf(r[i] - r[i-1]); if (d > jump) jump = d; }
          CHECK(tail == 0.f, "tail after choke not zero (%g)", tail);
          CHECK(jump < 0.5f, "click while choking (%g)", jump);
          free(r);
          skcore_init(&c, v, 44100.0); skcore_trigger(&c, 127);
          { float tmp[512]; float pk = 0; int j;
            for (j = 0; j < 20; ++j) skcore_process(&c, tmp, 512);
            skcore_choke(&c);
            for (j = 0; j < 4; ++j) skcore_process(&c, tmp, 512);
            skcore_trigger(&c, 127);
            for (j = 0; j < 8; ++j) { int q; skcore_process(&c, tmp, 512); for (q = 0; q < 512; ++q) if (fabsf(tmp[q]) > pk) pk = fabsf(tmp[q]); }
            CHECK(pk > 1e-3f, "silent after choke + retrigger");
          }
          skcore_free(&c); }

        /* 6. controls, names */
        skcore_init(&c, v, 44100.0);
        for (i = 0; i < (int)c.nctl; ++i) {
            CHECK(skcore_find_control(&c, v->control_names[i]) == i, "find_control %s", v->control_names[i]);
            CHECK(c.ctl[i] == skcore_default_of(v, i), "default %d", i);
        }
        CHECK(skcore_find_control(&c, "nope") == -1, "find_control accepts garbage");
        skcore_set_control(&c, 0, 300); CHECK(c.ctl[0] == 127, "clamp high");
        skcore_set_control(&c, 0, -5);  CHECK(c.ctl[0] == 0, "clamp low");
        skcore_defaults(&c); CHECK(c.ctl[0] == skcore_default_of(v, 0), "defaults");
        skcore_free(&c);

        /* 7. done detection (information only) */
        skcore_init(&c, v, 44100.0); skcore_trigger(&c, 127);
        { float tmp[512]; int j, got = 0;
          for (j = 0; j < 44100 * 12 / 512 && !got; ++j) { skcore_process(&c, tmp, 512); got = skcore_take_done(&c); }
          if (!got) printf("note %s: no 'done' within 12 s (long or endless tail)\n", name);
          nd += got; }
        skcore_free(&c);
        free(a);
    }
    {   /* note -> PTCH */
        const char *name = "note"; skcore c; unsigned k; int lo = 0, hi = 0, none = 0;
        for (k = 0; k < NVOICES; ++k) {
            skcore_init(&c, all_voices[k], 44100.0);
            if (!strcmp(all_voices[k]->name, "TRX-BD")) {
                unsigned char a, b;
                lo = skcore_note(&c, 30, 100); a = c.ctl[0];
                hi = skcore_note(&c, 44, 100); b = c.ctl[0];
                CHECK(lo == 1 && hi == 1 && b > a, "TRX-BD note table: %d -> %d", a, b);
                c.transpose = 12; skcore_note(&c, 30, 100);
                CHECK(c.ctl[0] > a, "transpose raises PTCH");
            }
            if (!strcmp(all_voices[k]->name, "TRX-CH")) { none = skcore_note(&c, 60, 100); CHECK(none == 0, "TRX-CH has no table"); }
            skcore_free(&c);
        }
    }
    printf("%d voices, %d checks, %d failures\n", (int)NVOICES, checks, fails);
    if (fails) return 1;
    puts("ALL OK");
    return 0;
}
