.POSIX:

all: run

run:
	@set -e; \
	repodir=`pwd`; \
	echo "Repository directory: $$repodir"; \
	\
	echo "Checking system for required applications"; \
	command -v python >/dev/null 2>&1 || { echo "Error: python not found."; exit 1; }; \
	command -v hw-probe >/dev/null 2>&1 || { echo "Error: hw-probe is not installed."; exit 1; }; \
	echo "Python and hw-probe are available."; \
	\
	tmpdir=`mktemp -d /tmp/hwprobe.XXXXXX` || exit 1; \
	trap 'rm -rf "$$tmpdir"' EXIT INT TERM; \
	echo "Using temp directory: $$tmpdir"; \
	\
	echo "Running probe. Please enter your root password."; \
	echo "============="; \
	su -m root -c "hw-probe -all -save $$tmpdir"; \
	echo "============="; \
	\
	echo "Extracting hardware dump..."; \
	cd "$$tmpdir"; \
	tar -xf *.tgz; \
	\
	echo "Running script..."; \
	python "$$repodir/main.py"; \
	\
	echo "Finished. Thank you for your contribution!"

.PHONY: all run
