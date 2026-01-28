import os
import re
from datetime import datetime
import shutil
from collections import deque

from pathlib import Path
import subprocess


#def generate_hardware_summary(ifconfig, hw_probe, output):
#    with open(output, "w") as out:
#        out.write("=== FreeBSD Hardware Status Info ===\n\n")


def get_device(input_file, search_term, output_file):
#Dynamic regex for finding the start of the string area
    subclass_pattern = re.compile(rf'subclass\s*=\s*{re.escape(search_term)}', re.IGNORECASE)
    class_pattern = re.compile(rf'class\s*=\s*{re.escape(search_term)}', re.IGNORECASE)
    header_pattern = re.compile(r'\S+@pci\d+:')  # Matches "none0@pci0:..."

    def search(target_pattern, label):
        found = False
        current_device_buffer = []

        with open(input_file, 'r') as f_in:
            for line in f_in:
                #reset if needed
                if header_pattern.search(line):
                    current_device_buffer = [line]
                else:
                    current_device_buffer.append(line)

                if target_pattern.search(line):
                    with open(output_file, 'a') as f_out:
                        f_out.write(f"--- Category: ({label}): '{search_term}' ---\n")
                        f_out.writelines(current_device_buffer)
                        f_out.write("\n")
                    found = True
                    current_device_buffer = []
        return found

    if not search(subclass_pattern, "subclass"):
        search(class_pattern, "class")

# Example:

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


hw_probe_dump = os.path.expanduser("~/hwify/hw.info/devices")
ifconfig_path = os.path.expanduser("~/hwify/hw.info/logs/ifconfig")
pciconf_path = os.path.expanduser("~/hwify/hw.info/logs/pciconf")

get_device(pciconf_path, 'vga', 'matches.txt')

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
'''
#test new function

#generate_hardware_summary(ifconfig_path, hw_probe_dump, filename_final)
#generate_verbose_input(devices_path, filename_final)
