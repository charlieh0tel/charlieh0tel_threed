PYTHON := python3
UV     := uv

OUT := out

DISC_FILES := $(OUT)/disc_120mm_cut_only.dxf \
              $(OUT)/disc_120mm_with_reference.dxf \
              $(OUT)/disc_120mm_preview.svg

CAP_FILES  := $(OUT)/mast_cap.step \
              $(OUT)/mast_cap_print.stl \
              $(OUT)/mast_cap_fit_ring.stl \
              $(OUT)/disc_120mm.step \
              $(OUT)/assembly.step

BOM := docs/BOM.md

all: $(DISC_FILES) $(CAP_FILES) $(BOM)

# Each script writes all of its files in one run (grouped targets, GNU Make >= 4.3).
$(DISC_FILES) &: src/generate.py
	$(PYTHON) src/generate.py --out $(OUT)

# cap.py takes every dimension from generate.py.
$(CAP_FILES) &: src/cap.py src/generate.py
	$(UV) run src/cap.py --out $(OUT)

# The BOM is tracked in git (it is a document, not a fabrication file), so clean leaves it.
$(BOM): src/generate.py
	$(PYTHON) src/generate.py --bom $@

check:
	$(PYTHON) src/generate.py --check
	$(UV) run src/cap.py --check

clean:
	rm -f $(DISC_FILES) $(CAP_FILES)

.PHONY: all check clean
