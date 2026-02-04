.POSIX:

TMPDIR := $(shell mktemp -d)

all: run

check:
	@echo "Checking system for required applications"
	@command -v python >/dev/null 2>&1 || { echo "Error: python not found."; exit 1; }
	@command -v hw-probe >/dev/null 2>&1 || { echo "Error: hw-probe is not installed."; exit 1; }
	@echo "Python and hw-probe are available."

probe: check
	@echo "Running probe. Please enter your root password."
	@echo "============="
	@echo "Using temp directory: $(TMPDIR)"
	su -m root -c "hw-probe -all -save $(TMPDIR)"
	@echo "============="

extract: probe
	@echo "Extracting hardware dump..."
	cd $(TMPDIR) && tar -xf *.tgz
	@echo "Extraction complete."

run: extract
	@echo "Running script..."
	cd $(TMPDIR) && python /path/to/your/repo/main.py
	@echo "Finished. Thank you for your contribution"
	rm -rf $(TMPDIR)

.PHONY: all check probe extract run
