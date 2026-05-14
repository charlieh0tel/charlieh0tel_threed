SCAD_FILES := $(wildcard *.scad)
STL_FILES  := $(SCAD_FILES:.scad=.stl)

OPENSCAD   := openscad

all: $(STL_FILES)

%.stl: %.scad
	$(OPENSCAD) --export-format binstl -o $@ $<

clean:
	rm -f $(STL_FILES)

.PHONY: all clean
