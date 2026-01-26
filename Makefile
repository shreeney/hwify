.POSIX:

BIN_DEPS = python hw-probe 

check-binaries:
	@for bin in $(BIN_DEPS); do \
		command -v $$bin >/dev/null 2>&1 || { echo "Error: $$bin is not installed. Please install these packages."; exit 1; }; \
	done
	@echo "All binaries verified."
