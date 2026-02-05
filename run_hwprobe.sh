#!/bin/sh
set -e

REPO_DIR=$(pwd)

TMPDIR=$(mktemp -d /tmp/hwprobe.XXXXXX)
trap 'rm -rf "$TMPDIR"' EXIT INT TERM

echo "Temporary directory: $TMPDIR"

echo "Checking for required programs..."
command -v python >/dev/null 2>&1 || { echo "Error: python not found."; exit 1; }
command -v hw-probe >/dev/null 2>&1 || { echo "Error: hw-probe not found."; exit 1; }
command -v kenv >/dev/null 2>&1 || { echo "Error: kenv not found."; exit 1; }
echo "All required programs are available."

echo "Running hardware probe..."
su -m root -c "hw-probe -all -save $TMPDIR"

echo "Extracting hardware dump..."
for tgz in "$TMPDIR"/*.tgz; do
    [ -e "$tgz" ] || continue
    tar -xf "$tgz" -C "$TMPDIR"
done

PYTHON_SCRIPT="$REPO_DIR/main.py"
echo "Running script..."
python "$PYTHON_SCRIPT" "$TMPDIR"

MAKER=$(kenv | grep '^smbios.system.maker=' | cut -d'=' -f2 | tr -d '"' | tr '[:upper:]' '[:lower:]')

if [ -z "$MAKER" ]; then
    echo "Error: Could not determine system maker."
    exit 1
fi

TARGET_DIR="$REPO_DIR/test_results/$MAKER"
mkdir -p "$TARGET_DIR"

FOUND=0
for f in "$TMPDIR"/*.txt; do
    if [ -e "$f" ]; then
        FOUND=1
        break
    fi
done

if [ "$FOUND" -eq 1 ]; then
    mv "$TMPDIR"/*.txt "$TARGET_DIR/"
else
    echo "Warning: No .txt files found to move."
fi

echo "Finished. Thank you for your contribution!"

