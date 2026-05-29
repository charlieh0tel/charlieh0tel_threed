OPENSCAD := openscad

LIBS      := params.scad collar.scad ear_knuckle.scad
TOP_SCADS := back_clamp.scad front_clamp.scad pin.scad
STL_FILES := $(TOP_SCADS:.scad=.stl)

all: $(STL_FILES)

%.stl: %.scad $(LIBS)
	$(OPENSCAD) --export-format binstl -o $@ $<

clean:
	rm -f $(STL_FILES)

.PHONY: all clean
