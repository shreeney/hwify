#!/bin/sh

set -e

REPOi_DIR=$(pwd)
TMPDIR=$(mktemp -d /tmp/hwprobe.XXXXXX) #posix temp directory format
trap 'rm -rf "$TMPDIR"' EXIT INT TERM

echo "Temporary directory: $TMPDIR"

echo "Checking for required programs"
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 not found."; exit 1; }
command -v hw-probe >/dev/null 2>&1 || { echo "Error: hw-probe not found."; exit 1; }
command -v kenv >/dev/null 2>&1 || { echo "Error: kenv not found."; exit 1; }
echo "All required programs are available."

echo "Running hardware probe..."
su -m root -c "hw-probe -all -save $TMPDIR"

echo "Extracting .tgz file..."
tar -xf "$TMPDIR"/*.tgz -C "$TMPDIR"

echo "Running Python script..."
python3 "$REPO_DIR/main.py" "$TMPDIR"

MAKER=$(kenv | grep '^smbios.system.maker=' | cut -d'=' -f2 | tr -d '"' | tr '[:upper:]' '[:lower:]')

if [ -z "$MAKER" ]; then
    echo "Could not determine system make"
    exit 1
fi

TARGET_DIR="$REPO_DIR/test_results/$MAKER"
mkdir -p "$TARGET_DIR"

echo "Moving generated files to $TARGET_DIR"
if compgen -G "$TMPDIR/*.txt" > /dev/null; then
    mv "$TMPDIR"/*.txt "$TARGET_DIR/"
else
    echo "Warning: no files found to move."
fi

echo "Finished. Thank you for your contribution!"

