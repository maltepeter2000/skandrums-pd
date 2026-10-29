/* SPDX-License-Identifier: CC0-1.0
 * Renders every voice with a PTCH control at PTCH=0,4,..,124,127 (raw voice, 44.1 kHz, 0.5 s)
 * into out/ptch/<NAME>.f32 (33 x 22050 floats). tools/ptch_analyze.py turns that into note tables. */
#include "skcore.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "voices_gen.h"
#define N 22050
int main(void)
{
    unsigned i, k, p;
    static float buf[N];
    for (i = 0; i < sizeof all_voices / sizeof *all_voices; ++i) {
        const mdkit_voice *v = all_voices[i];
        int pi = -1; char fn[128]; FILE *f; void *st;
        for (k = 0; k < v->control_count; ++k) if (!strcmp(v->control_names[k], "PTCH")) pi = (int)k;
        if (pi < 0) continue;
        snprintf(fn, sizeof fn, "out/ptch/%s.f32", v->name);
        f = fopen(fn, "wb");
        for (p = 0; p <= 33; ++p) {
            unsigned val = p < 32 ? p * 4 : (p == 32 ? 124 : 127);
            if (p == 33) break;
            st = calloc(1, v->state_bytes);
            v->init(st);
            for (k = 0; k < v->control_count; ++k) v->set_control(st, k, skcore_default_of(v, k));
            v->set_control(st, (unsigned)pi, val);
            v->trigger(st);
            for (k = 0; k < N; k += 100) v->render(st, buf + k, (unsigned)(N - k < 100 ? N - k : 100));
            fwrite(buf, sizeof(float), N, f);
            free(st);
        }
        fclose(f);
        printf("%s idx=%d\n", v->name, pi);
    }
    return 0;
}
