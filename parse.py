import json
import re
import argparse
from pathlib import Path

#logic for taking in cmd line params
parser = argparse.ArgumentParser(description="Hw-probe file")
parser.add_argument(
    "filepath",
    type=Path,
    help="Path to the input file"
)

args = parser.parse_args()

file_path = args.filepath

if not file_path.exists():
    print(f"path not found: {file_path}")
    exit(1)

print(f"Reading file at: {file_path}")


def parse_hardware_status(path):
    data = {} #empty dict
    current_section = None
    current_device = None

    device_header_re = re.compile(r"Device (\d+) Status: (\w+)")
    key_value_re = re.compile(r"(\w+)\s*=\s*'?(.*?)'?$")

    with open(path) as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("- "):
                current_section = line[2:]
                data[current_section] = []
                continue

            m = device_header_re.match(line)
            if m:
                current_device = {
                    "device_number": int(m.group(1)),
                    "status": m.group(2)
                }
                data[current_section].append(current_device)
                continue

            if "@" in line and "class=" in line:
                identifier, rest = line.split(":", 1)
                current_device["identifier"] = identifier.strip()

                for part in rest.split():
                    if "=" in part:
                        k, v = part.split("=", 1)
                        current_device[k] = v
                continue

            m = key_value_re.match(line)
            if m and current_device is not None:
                key, value = m.groups()
                current_device[key] = value
                continue

    return data

parsed = parse_hardware_status(file_path)

with open("hardware.json", "w") as file:
    json.dump(parsed, file, indent=2)
