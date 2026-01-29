import os
import re
from datetime import datetime
#import shutil
#from collections import deque

#from pathlib import Path
import subprocess

hw_probe_dump = os.path.expanduser("~/hwify/hw.info/devices")
ifconfig_path = os.path.expanduser("~/hwify/hw.info/logs/ifconfig")
pciconf_path = os.path.expanduser("~/hwify/hw.info/logs/pciconf")


def get_device(input_file, search_term):
    subclass_pat = re.compile(rf'subclass\s*=\s*{re.escape(search_term)}', re.IGNORECASE)
    class_pat = re.compile(rf'class\s*=\s*{re.escape(search_term)}', re.IGNORECASE)
    header_pat = re.compile(r'\S+@pci\d+:')

    def scan(pattern):
        matches = []
        buffer = []
        try:
            with open(input_file, 'r') as f_in:
                for line in f_in:
                    if header_pat.search(line):
                        buffer = [line]
                    else:
                        buffer.append(line)

                    if pattern.search(line):
                        matches.append("".join(buffer))
                        buffer = []
        except FileNotFoundError:
            return []
        return matches

    results = scan(subclass_pat)
    if not results:
        results = scan(class_pat)

    return results


def generate_hardware_summary(pciconf, hw_probe, output):
    categories = {
        "Graphics": ("vga", "vga"),
        "Networking": ("network", "network"),
        "Audio": ("hda", "hda"),
        "SSD": ("storage", "storage"),
        "USB Ports": ("usb", "usb"),
        "Bluetooth": ("bluetooth", "bluetooth")
    }

    with open(output, "w") as out:
        out.write("=== FreeBSD Hardware Status Info ===\n\n")

        for label, (pci_key, probe_key) in categories.items():

            pci_blocks = get_device(pciconf, pci_key)
            status = get_hw_status(hw_probe, probe_key)

            out.write(f"- {label}\n")

            if pci_blocks:
                out.write(f"  Status: {status.upper()}\n")
                for i, block in enumerate(pci_blocks, 1):
                    prefix = f"  Device {i}:" if len(pci_blocks) > 1 else "  Details:"
                    indented = "    " + block.replace("\n", "\n    ").strip()
                    out.write(f"{prefix}\n{indented}\n")
            else:
                out.write("  Status: NOT DETECTED\n")

            out.write("\n" + "-" * 20 + "\n\n")


def get_hw_status(probe_file, category_name):
    statuses = ['works', 'failed', 'detected', 'limited', 'malfunc']
    status_pattern = re.compile(rf"\b({'|'.join(statuses)})\b", re.IGNORECASE)
    try:
        with open(probe_file, 'r') as f:
            for line in f:
                if category_name.lower() in line.lower():
                    match = status_pattern.search(line)
                    if match:
                        return match.group(1).lower() # Returns just the status string
        return "not found"
    except FileNotFoundError:
        return "file error"


input_string = "kenv | grep smbios.system.product"
filename_final  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #fallback filename for time stamp in case smbios is not present on the machine
result = subprocess.run(input_string, capture_output=True, text=True, shell=True)
output_string = result.stdout
filename = re.search('"([^"]*)"', output_string)

if filename:
    filename = filename.group(1)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename_final = f"{filename}_{timestamp}.txt"

#generate file name
input_string = "kenv | grep smbios.system.product"
filename_final  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #fallback filename for time stamp in case smbios is not present on the machine
result = subprocess.run(input_string, capture_output=True, text=True, shell=True)
output_string = result.stdout
filename = re.search('"([^"]*)"', output_string)

if filename:
    filename = filename.group(1)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename_final = f"{filename}_{timestamp}.txt"

generate_hardware_summary(pciconf_path, hw_probe_dump, filename_final)
