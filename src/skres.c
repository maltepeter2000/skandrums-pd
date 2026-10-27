#include <math.h>
#include <string.h>
#include "skres.h"

#define H (SKRES_TAPS / 2)
#ifndef SKRES_GUARD_HZ
#define SKRES_GUARD_HZ 1700.0   /* kernel cutoff distance below host Nyquist */
#endif

static double bessel_i0(double x)
{
    double sum = 1.0, term = 1.0;
    int k;
    for (k = 1; k < 50; ++k) {
        double h = x / (2.0 * k);
        term *= h * h;
        sum += term;
    }
    return sum;
}

static void build_kernel(skres *r)
{
    const double beta = 8.0;                       /* Kaiser, ~80 dB stopband */
    double fc;
    int p, k;
    if (r->host_sr < SKRES_NATIVE_RATE)
        fc = (r->host_sr * 0.5 - SKRES_GUARD_HZ) / (SKRES_NATIVE_RATE * 0.5);
    else
        fc = 0.98;
    if (fc < 0.1) fc = 0.1;
    for (p = 0; p <= SKRES_PHASES; ++p) {
        double f = (double)p / SKRES_PHASES, sum = 0.0;
        float *row = r->kernel + (size_t)p * SKRES_TAPS;
        for (k = 0; k < SKRES_TAPS; ++k) {
            double tt = k - (H - 1) - f;
            double arg = 3.14159265358979323846 * fc * tt;
            double s = fabs(arg) < 1e-9 ? 1.0 : sin(arg) / arg;
            double rr = tt / H;
            double w = fabs(rr) >= 1.0 ? 0.0 :
                bessel_i0(beta * sqrt(1.0 - rr * rr)) / bessel_i0(beta);
            double v = fc * s * w;
            row[k] = (float)v;
            sum += v;
        }
        for (k = 0; k < SKRES_TAPS; ++k)
            row[k] = (float)(row[k] / sum);
    }
}

void skres_reset(skres *r)
{
    memset(r->buf, 0, sizeof r->buf);
    r->count = H - 1;               /* H-1 zeros of history before frame 0 */
    r->pos = H - 1;
}

void skres_set_samplerate(skres *r, double host_sr)
{
    if (host_sr < 8000.0) host_sr = SKRES_NATIVE_RATE;
    if (r->host_sr > 0.0 && fabs(host_sr - r->host_sr) < 0.5)
        return;                     /* unchanged: keep resampler state */
    r->host_sr = host_sr;
    r->bypass = fabs(host_sr - SKRES_NATIVE_RATE) < 0.5;
    r->step = SKRES_NATIVE_RATE / host_sr;
    if (!r->bypass) build_kernel(r);
    skres_reset(r);
}

void skres_init(skres *r, double host_sr)
{
    memset(r, 0, sizeof *r);
    skres_set_samplerate(r, host_sr);
}

static void compact(skres *r)
{
    int shift = (int)r->pos - (H - 1);
    if (shift > 0) {
        memmove(r->buf, r->buf + shift, (size_t)(r->count - shift) * sizeof(float));
        r->count -= shift;
        r->pos -= shift;
    }
}

void skres_process(skres *r, float *out, int frames,
                   skres_render_fn fn, void *ctx)
{
    int i;
    if (r->bypass) {
        int done = 0;
        while (done < frames) {
            int n = frames - done;
            if (n > SKRES_MAXBLOCK) n = SKRES_MAXBLOCK;
            fn(ctx, out + done, n);
            done += n;
        }
        return;
    }
    for (i = 0; i < frames; ++i) {
        int ip, k;
        double ph;
        int i0;
        float a, acc = 0.f;
        const float *k0, *k1, *x;
        ip = (int)r->pos;
        while (r->count < ip + H + 1) {
            if (r->count + SKRES_CHUNK > SKRES_BUFLEN) {
                compact(r);
                ip = (int)r->pos;
            }
            fn(ctx, r->buf + r->count, SKRES_CHUNK);
            r->count += SKRES_CHUNK;
        }
        ph = (r->pos - ip) * SKRES_PHASES;
        i0 = (int)ph;
        a = (float)(ph - i0);
        k0 = r->kernel + (size_t)i0 * SKRES_TAPS;
        k1 = k0 + SKRES_TAPS;
        x = r->buf + ip - (H - 1);
        for (k = 0; k < SKRES_TAPS; ++k)
            acc += x[k] * (k0[k] + a * (k1[k] - k0[k]));
        out[i] = acc;
        r->pos += r->step;
    }
}
