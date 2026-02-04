.POSIX:

all: run

run:
	@set -e; \
	\
	repodir=`pwd`; \
	echo "Repository directory: $$repodir"; \
	\
	echo "Checking for required applications..."; \
	command -v python >/dev/null 2>&1 || { echo "Error: python not found."; exit 1; }; \
	command -v hw-probe >/dev/null 2>&1 || { echo "Error: hw-probe not found."; exit 1; }; \
	echo "python and hw-probe are available."; \
	\
	tmpdir=`mktemp -d /tmp/hwprobe.XXXXXX` || exit 1; \
	trap 'rm -rf "$$tmpdir"' EXIT INT TERM; \
	echo "Created temp dir: $$tmpdir"; \
	\
	echo "Running probe. Please enter your root password."; \
	echo "============="; \
	su -m root -c "hw-probe -all -save $$tmpdir"; \
	echo "============="; \
	\
	echo "Extracting file"; \
	cd "$$tmpdir"; \
	tar -xf *.tgz; \
	\
	echo "Running script"; \
	python "$$repodir/main.py" "$$tmpdir"; \
	\
	echo "Moving into test_results directory"; \
	mkdir -p "$$repodir/test_results"; \
	set -- "$$tmpdir"/*.txt; \
	if [ -e "$$1" ]; then \
		mv "$$@" "$$repodir/test_results/"; \
	else \
		echo "Error"; \
	fi; \
	\
	echo "Finished. Thank you for your contribution!"

.PHONY: all run
