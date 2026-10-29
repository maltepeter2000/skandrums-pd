/* SPDX-License-Identifier: CC0-1.0
 * Prints one line per mdkit voice: NAME|id|controls|state_bytes|CTL=default,...
 * Used by tools/gen_help.py to generate the help patches. */
#include "skcore.h"
#include <stdio.h>
#include "voices_gen.h"
int main(void)
{
    unsigned i, k;
    for (i = 0; i < sizeof all_voices / sizeof *all_voices; ++i) {
        const mdkit_voice *x = all_voices[i];
        printf("%s|%u|%u|%zu|", x->name, x->machine_id, x->control_count, x->state_bytes);
        for (k = 0; k < x->control_count; ++k)
            printf("%s=%u%s", x->control_names[k],
                   skcore_default_of(x, k),
                   k + 1 < x->control_count ? "," : "");
        puts("");
    }
    return 0;
}
