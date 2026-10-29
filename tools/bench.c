/* SPDX-License-Identifier: CC0-1.0
 * CPU benchmark per voice. Renders 20 s at 44.1 kHz in small blocks with a
 * trigger every 500 ms and prints average CPU load and the worst block.
 * usage: ./out/bench [blocksize=32] */
#define _POSIX_C_SOURCE 199309L
#include "skcore.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "voices_gen.h"

static double now_us(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e6 + t.tv_nsec * 1e-3;
}

int main(int argc, char **argv)
{
    int bs = argc > 1 ? atoi(argv[1]) : 32;
    const double sr = 44100.0;
    const long total = (long)(sr * 20.0), every = (long)(sr * 0.5);
    float buf[1024];
    unsigned i;
    double sum_all = 0;
    if (bs < 1 || bs > 1024) bs = 32;
    printf("block %d frames, budget %.0f us per block\n", bs, bs / sr * 1e6);
    printf("%-8s %8s %12s %12s\n", "voice", "avg %", "worst us", "worst %bud");
    for (i = 0; i < sizeof all_voices / sizeof *all_voices; ++i) {
        skcore c;
        long pos, next = 0;
        double spent = 0, worst = 0;
        if (skcore_init(&c, all_voices[i], sr)) return 1;
        for (pos = 0; pos + bs <= total; pos += bs) {
            double t0, dt;
            t0 = now_us();
            if (pos >= next) { skcore_trigger(&c, 100); next += every; }
            skcore_process(&c, buf, bs);
            dt = now_us() - t0;
            spent += dt;
            if (dt > worst) worst = dt;
        }
        {
            double avg = spent / (total / sr * 1e6) * 100.0;
            sum_all += avg;
            printf("%-8s %7.2f%% %12.1f %11.0f%%\n", all_voices[i]->name, avg, worst,
                   worst / (bs / sr * 1e6) * 100.0);
        }
        skcore_free(&c);
    }
    printf("sum of all voices: %.1f%%\n", sum_all);
    return 0;
}
