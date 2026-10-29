# skandrums-pd: one Pure Data external per mdkit voice (30 objects).
#   make                  build all voices into out/
#   make VOICES="trx/b2 trx/ch trx/oh"   build only some
#   make test             core tests without Pd
#   make install          copy into the user externals folder
#   make PDINC=/path/to/dir/with/m_pd.h    if auto-detection fails
.DEFAULT_GOAL := all
UNAME := $(shell uname -s)

CFLAGS += -O2 -std=gnu99 -Wall -Wno-unused-parameter -Wno-misleading-indentation -fPIC -fvisibility=hidden \
          -Isrc -Imdkit/include

ifeq ($(UNAME),Darwin)
  EXT      = pd_darwin
  PDINC   ?= $(lastword $(sort $(wildcard /Applications/Pd-*.app/Contents/Resources/src)))
  ARCH    ?= -arch arm64 -arch x86_64
  CFLAGS  += $(ARCH) -mmacosx-version-min=10.13
  LDFLAGS += -bundle -undefined dynamic_lookup $(ARCH)
  INSTALLDIR ?= $(HOME)/Documents/Pd/externals
else
  EXT      = pd_linux
  PDINC   ?= /usr/include/pd
  LDFLAGS += -shared -fPIC
  INSTALLDIR ?= $(HOME)/pd-externals
endif

# every mdkit/src/<family>/<code>/mdkit_<family>_<code>.c is a voice
ALL_VOICES := $(sort $(patsubst mdkit/src/%,%,$(patsubst %/,%,$(dir $(wildcard mdkit/src/*/*/mdkit_*.c)))))
VOICES ?= $(ALL_VOICES)

COMMON = src/skdrums_tilde.c src/skcore.c src/skres.c
HDRS   = src/skcore.h src/skres.h

OUTS :=
define VOICE_RULE
OUTS += out/$(subst /,,$(1))~.$(EXT)
out/$(subst /,,$(1))~.$(EXT): $(COMMON) $(HDRS) mdkit/src/$(1)/mdkit_$(subst /,_,$(1)).c | out
	$$(CC) $$(CFLAGS) -I$$(PDINC) -Imdkit/src/$(1) \
	  -DSK_OBJ_NAME='"$(subst /,,$(1))~"' -DSK_SHORT='"$(subst /,,$(1))"' \
	  -DSK_SETUP=$(subst /,,$(1))_tilde_setup -DSK_VOICE=mdkit_voice_$(subst /,_,$(1)) \
	  -DSK_HEADER='"mdkit_$(subst /,_,$(1)).h"' \
	  $(COMMON) mdkit/src/$(1)/mdkit_$(subst /,_,$(1)).c -o $$@ $$(LDFLAGS) -lm
endef
$(foreach v,$(VOICES),$(eval $(call VOICE_RULE,$(v))))

all: $(OUTS)

out:
	mkdir -p out

# --- tests (no Pd needed) ---
out/voices_gen.h: | out
	@{ for v in $(ALL_VOICES); do echo "#include \"mdkit_$$(echo $$v | tr / _).h\""; done; \
	   echo "static const mdkit_voice *const all_voices[] = {"; \
	   for v in $(ALL_VOICES); do echo "  &mdkit_voice_$$(echo $$v | tr / _),"; done; \
	   echo "};"; } > $@

VOICE_INC = $(foreach v,$(ALL_VOICES),-Imdkit/src/$(v))
VOICE_SRC = $(foreach v,$(ALL_VOICES),mdkit/src/$(v)/mdkit_$(subst /,_,$(v)).c)

out/test_core: tests/test_core.c src/skcore.c src/skres.c $(HDRS) out/voices_gen.h $(VOICE_SRC)
	$(CC) -std=gnu99 -O2 -Wall -Wno-unused-parameter -Wno-misleading-indentation -Isrc -Imdkit/include -Iout $(VOICE_INC) \
	  tests/test_core.c src/skcore.c src/skres.c $(VOICE_SRC) -lm -o $@

test: out/test_core
	./out/test_core

out/dump_voices: tools/dump_voices.c src/skcore.c src/skres.c out/voices_gen.h $(VOICE_SRC)
	$(CC) -std=gnu99 -O2 -Wno-misleading-indentation -Isrc -Imdkit/include -Iout $(VOICE_INC) \
	  tools/dump_voices.c src/skcore.c src/skres.c $(VOICE_SRC) -lm -o $@

# generate help patches (needs python3)
help: out/dump_voices
	./out/dump_voices > out/voices.txt
	python3 tools/gen_help.py out/voices.txt help
	python3 tools/gen_skpreset.py pd/skpreset.pd

install: all
	mkdir -p "$(INSTALLDIR)"
	cp out/*.$(EXT) "$(INSTALLDIR)/"
	-cp help/*.pd pd/*.pd "$(INSTALLDIR)/" 2>/dev/null

clean:
	rm -rf out

.PHONY: all test help install clean
