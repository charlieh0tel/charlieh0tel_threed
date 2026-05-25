OPENSCAD := openscad

SCAD       := feeder.scad
PARTS      := back_wall_mount front_clamp print_pins
STL_FILES  := $(addprefix feeder_,$(addsuffix .stl,$(PARTS)))

all: $(STL_FILES)

feeder_%.stl: $(SCAD)
	$(OPENSCAD) --export-format binstl -D 'part="$*"' -o $@ $<

clean:
	rm -f $(STL_FILES)

.PHONY: all clean
