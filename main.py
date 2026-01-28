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

def get_device(input_file, subclass_to_find, output_file):
    pattern = re.compile(rf'subclass\s*=\s*{re.escape(subclass_to_find)}', re.IGNORECASE) #takes in subclass and creates the dynamic regex
    context_buffer = deque(maxlen=5)

    with open(input_file, 'r') as f_in, open(output_file, 'a') as f_out:
        for line in f_in:
            context_buffer.append(line)
            if pattern.search(line):
                f_out.write(f"--- Subclass: '{subclass_to_find}' ---\n")
                f_out.writelines(context_buffer)
                f_out.write("\n")  # Add extra space between separate matches

                # Optional: clear buffer to prevent overlapping if devices are back-to-back
                context_buffer.clear()

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
