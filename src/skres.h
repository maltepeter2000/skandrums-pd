/* skres: host-rate adapter for mdkit voices (no Pd dependency).
 *
 * The mdkit voices run at a fixed 44.1 kHz. If the host runs at another rate
 * the output is converted with a windowed-sinc (Kaiser) polyphase resampler.
 * At exactly 44.1 kHz (+-0.5 Hz) the voice output is passed through
 * bit-exactly.
 */
#ifndef SKRES_H
#define SKRES_H

#ifndef SKRES_NATIVE_RATE
#define SKRES_NATIVE_RATE 44100.0
#endif
#ifndef SKRES_TAPS
#define SKRES_TAPS    64      /* sinc kernel length (even) */
#endif
#define SKRES_PHASES  512     /* sub-sample kernel phases */
#define SKRES_CHUNK   16      /* voice render granularity in the resampling path */
#define SKRES_BUFLEN  512     /* input history / lookahead buffer */
#define SKRES_MAXBLOCK 128    /* largest block handed to the render callback */

/* Render `frames` (<= SKRES_MAXBLOCK) native-rate frames as float (+-1.0). */
typedef void (*skres_render_fn)(void *ctx, float *dst, int frames);

typedef struct {
    double host_sr;
    int    bypass;            /* host rate == native-rate */
    double step;              /* input frames per output frame */
    double pos;               /* read position inside buf */
    int    count;             /* valid frames in buf */
    float  buf[SKRES_BUFLEN];
    float  kernel[(SKRES_PHASES + 1) * SKRES_TAPS];
} skres;

void skres_init(skres *r, double host_sr);
void skres_set_samplerate(skres *r, double host_sr);  /* no-op if unchanged */
void skres_reset(skres *r);                           /* clear filter history */
void skres_process(skres *r, float *out, int frames,
                   skres_render_fn fn, void *ctx);

#endif
