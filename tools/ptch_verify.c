/* SPDX-License-Identifier: CC0-1.0
 * Renders skcore_note(n) for every voice that has a table and every note in its range (step 2),
 * writes out/ptchv/<NAME>.f32 (+ <NAME>.txt with the note list). tools/ptch_verify.py checks the pitch. */
#include "skcore.h"
#include "skptch.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "voices_gen.h"
#define N 22050
int main(void)
{
    unsigned i, t, k; static float buf[N];
    for (t = 0; t < sizeof sk_ptch_tables / sizeof *sk_ptch_tables; ++t) {
        const mdkit_voice *v = NULL; char fn[128]; FILE *f, *g; int n;
        for (i = 0; i < sizeof all_voices / sizeof *all_voices; ++i) if (!strcmp(all_voices[i]->name, sk_ptch_tables[t].name)) v = all_voices[i];
        if (!v) continue;
        snprintf(fn, sizeof fn, "out/ptchv/%s.f32", v->name); f = fopen(fn, "wb");
        snprintf(fn, sizeof fn, "out/ptchv/%s.txt", v->name); g = fopen(fn, "w");
        for (n = sk_ptch_tables[t].lo; n <= sk_ptch_tables[t].hi; n += 2) {
            skcore c; skcore_init(&c, v, 44100.0);
            skcore_note(&c, n, 127);
            for (k = 0; k < N; k += 64) skcore_process(&c, buf + k, (int)(N - k < 64 ? N - k : 64));
            fwrite(buf, sizeof(float), N, f); fprintf(g, "%d\n", n);
            skcore_free(&c);
        }
        fclose(f); fclose(g);
    }
    return 0;
}
