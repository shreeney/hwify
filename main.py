import os
import re
from datetime import datetime
import shutil


from collections import defaultdict #import defaultdict
from pathlib import Path
import subprocess
#dictionary for all different categories of devices
HARDWARE_MAP = {
    "Graphics": ["i915", "display", "nvidia", "amdgpu", "radeon"],
    "Wi-Fi": ["wireless", "wlan", "802.11", "iwlwifi", "ath9k","rtw88","rtw89","mt76", "ath11k", "iwm", "iwx"],
    "Audio": ["audio", "sound", "hda", "codec"],
    "Card Reader": ["card reader", "sdhc", "rtsx"],
    "Storage": ["sda", "nvme", "ssd"],
    "Bluetooth": ["bluetooth", "btusb"],
    "Ethernet": ["ethernet", "rtl8111"]
}

def generate_hardware_summary(input_file, output_file):
    found_details = defaultdict(list)
    failed = {category: False for category in HARDWARE_MAP}

    with open(input_file, "r") as file:
        for line in file:
            line_lower = line.lower()
            for category, keywords in HARDWARE_MAP.items():
                if any(kw in line_lower for kw in keywords):
                    found_details[category].append(line.strip())
                    if "failed" in line_lower:
                        failed[category] = True

    with open(output_file, "w") as out:
        out.write("=== FreeBSD Hardware Status Info ===\n\n")

        for category in HARDWARE_MAP:
            is_detected = category in found_details
            has_failed = failed[category]

            if not is_detected:
                status_text = "Not detected"
            elif has_failed:
                status_text = "Failed"
            else:
                status_text = "Working"

            out.write(f"{category}: {status_text}\n")

            if is_detected:
                for detail in found_details[category]:
                    marker = " [!] " if "failed" in detail.lower() else "  - "
                    out.write(f"{marker}{detail}\n")
            out.write("-" * 40 + "\n")
        out.write("\n\n=== FreeBSD Advanced Information ===\n\n")


def generate_dev_info(input_file, output_file): #use ssid keyword in git cosearch
    with open(output_file, 'a') as out:
        out.write("\n")
        #start ifconfig subprocess
        cmd1 = "ifconfig | grep ssid"
        cmd2 = "ifconfig | grep media"
        with open(output_file,"a") as file:
            subprocess.run(cmd1, shell=True, stdout=out)
            subprocess.run(cmd2, shell=True, stdout=out)
    current_dir = Path(__file__).parent.absolute()

    source = current_dir / output_file
    target = current_dir / "test_results"

    target.mkdir(parents=True, exist_ok=True)

    shutil.move(str(source), str(target))

hardware_summary_path = os.path.expanduser("~/hwify/hw.info/devices")
devices_path = os.path.expanduser("~/hwify/hw.info/logs/ifconfig")


#filename logic
input_string = "kenv | grep smbios.system.product"
filename_final  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #fallback filename for time stamp in case smbios is not present on the machine
result = subprocess.run(input_string, capture_output=True, text=True, shell=True)
output_string = result.stdout
filename = re.search('"([^"]*)"', output_string)

if filename:
    filename = filename.group(1)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    filename_final = f"{filename}_{timestamp}.txt"


generate_hardware_summary(hardware_summary_path, filename_final)
generate_dev_info(devices_path, filename_final)