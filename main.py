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

def generate_hardware_summary(pciconf, hw_probe, output):
    with open(output, "a") as out:
        out.write("=== FreeBSD Hardware Status Info ===\n\n")
        #Categories to test: Graphics, Wi-Fi, Audio, Card Reader, Ethernet, Bluetooth

        out.write("- Graphics:")
        graphics = get_device(pciconf, 'graphics', output)

        if graphics is not None:
            out.write(get_hw_status(hw_probe, 'graphics'))
        else:
            out.write("Not detected")

        out.write("\n")
        out.write("- Networking")

        network = get_device(pciconf, 'network', output)
        if network is not None:
            out.write(get_hw_status(hw_probe, 'network'))
        else:
            out.write("Not detected")

        out.write("\n")
        out.write("- Audio")

        audio = get_device(pciconf, 'hda', output)
        if audio is not None:
            out.write(get_hw_status(hw_probe,'hda'))
        else:
            out.write("Not detected")

        out.write("\n")
        out.write("- Storage Devices")

        storage = get_device(pciconf, 'mass storage', output)
        if storage is not None:
            out.write(get_hw_status(hw_probe, 'storage'))
        else:
            out.write("Not detected")


def get_device(input_file, search_term, output_file):
    subclass_pat = re.compile(rf'subclass\s*=\s*{re.escape(search_term)}', re.IGNORECASE)
    class_pat = re.compile(rf'class\s*=\s*{re.escape(search_term)}', re.IGNORECASE)
    header_pat = re.compile(r'\S+@pci\d+:')

    def scan(pattern):
        found_in_scan = False
        buffer = []
        with open(input_file, 'r') as f_in:
            for line in f_in:
                if header_pat.search(line):
                    buffer = [line]
                else:
                    buffer.append(line)

                if pattern.search(line):
                    with open(output_file, 'a') as f_out:
                        f_out.writelines(buffer)
                        f_out.write("\n")
                    found_in_scan = True
                    buffer = []
        return found_in_scan

    found = scan(subclass_pat)
    if not found:
        found = scan(class_pat)

    return found

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


#filename
input_string = "kenv | grep smbios.system.product"
filename_final  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #fallback filename for time stamp in case smbios is not present on the machine
result = subprocess.run(input_string, capture_output=True, text=True, shell=True)
output_string = result.stdout
filename = re.search('"([^"]*)"', output_string)

if filename:
    filename = filename.group(1)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename_final = f"{filename}_{timestamp}.txt"

generate_hardware_summary(ifconfig_path, hw_probe_dump, filename_final)
'''
def generate_ifconfig_info(input_file, output_file): #use ssid keyword in git cosearch
    with open(output_file, 'a') as out:
        out.write("\n")
        #start ifconfig subprocess
        cmd1 = f"cat {input_file} | grep ssid"
        cmd2 = f"cat {input_file} | grep media"
        out.write("\n")
        subprocess.run(cmd1, shell=True, stdout=out)
        subprocess.run(cmd2, shell=True, stdout=out)

    current_dir = Path(__file__).parent.absolute()

    source = current_dir / output_file
    target = current_dir / "test_results"

    target.mkdir(parents=True, exist_ok=True)

    shutil.move(str(source), str(target))

def generate_disk_info(input_file,output_file):
    with open(output_file)

'''




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

#test new function

#generate_hardware_summary(ifconfig_path, hw_probe_dump, filename_final)
#generate_verbose_input(devices_path, filename_final)
