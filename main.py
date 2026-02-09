import sys
from pathlib import Path
import re
from datetime import datetime
import subprocess

def generate_html_output(device_data, output):
    # HTML table header
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Laptop Compatibility Information</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px 12px; border: 1px solid #ccc; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            h1 {{ text-align: center; }}
        </style>
    </head>
    <body>
        <h1>Laptop Compatibility Information</h1>
        <table>
            <thead>
                <tr>
                    <th>Hardware Name</th>
                    <th>Graphics</th>
                    <th>Networking</th>
                    <th>Audio</th>
                    <th>Storage</th>
                    <th>USB Ports</th>
                </tr>
            </thead>
            <tbody>
    """

    html_content += f"""
        <tr>
            <td>{device_data['name']}</td>
            <td>{device_data['Graphics']}</td>
            <td>{device_data['Networking']}</td>
            <td>{device_data['Audio']}</td>
            <td>{device_data['Storage']}</td>
            <td>{device_data['USB Ports']}</td>
        </tr>
    """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    with open(output, "w") as out:
        out.write(html_content)


def parse_device_data(hw_probe_dump, ifconfig_path, pciconf_path):
    # Example categories
    categories = {
        "Graphics": (("vga", "display"), "graphics card"),
        "Networking": ("network", "network"),
        "Audio": (("hda", "multimedia"), "hda"),
        "Storage": ("mass storage", "storage"),
        "USB Ports": ("usb", "usb"),
        "Bluetooth": ("bluetooth", "bluetooth")
    }

    # Extract hardware information from the logs
    def get_device(input_file, search_terms):
        if isinstance(search_terms, str):
            search_terms = [search_terms]
        combined_pattern = "|".join([re.escape(term) for term in search_terms])

        subclass_pat = re.compile(rf'subclass\s*=\s*({combined_pattern})', re.IGNORECASE)
        class_pat = re.compile(rf'class\s*=\s*({combined_pattern})', re.IGNORECASE)

        def scan(pattern):
            matches = []
            buffer = []
            try:
                with open(input_file, 'r') as f_in:
                    for line in f_in:
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

    # Now let's gather the data for each category based on the probes
    device_data = {"name": filename, "Graphics": get_device(hw_probe_dump, "graphics card"),
                   "Networking": get_device(hw_probe_dump, "network"), "Audio": "Not Detected",
                   "Storage": "Not Detected", "USB Ports": "Not Detected"}

    # Extract actual data from hw_probe_dump, pciconf, and other files
    # First, we'll extract relevant hardware info from hw_probe_dump

    # Now let's extract additional data from the other probe logs (ifconfig, pciconf)
    for label, (pci_key, probe_key) in categories.items():
        pci_blocks = get_device(pciconf_path, pci_key)
        if pci_blocks:
            device_data[label] = ', '.join([block.strip() for block in pci_blocks])

    # Example: Add networking info from the ifconfig file
    networking_info = get_device(ifconfig_path, "network")
    if networking_info:
        device_data["Networking"] = ', '.join(networking_info)

    return device_data


def generate_hardware_summary(ifconfig, pciconf, hw_probe, output):
    pass

if len(sys.argv) >= 2:
    tmpdir = Path(sys.argv[1])
else:
    tmpdir = Path.home() / "hwify"  # default if no temp directory is specified

base_hwinfo = tmpdir / "hw.info"
hw_probe_dump = base_hwinfo / "devices"
ifconfig_path = base_hwinfo / "logs" / "ifconfig"
pciconf_path = base_hwinfo / "logs" / "pciconf"
uname_path = base_hwinfo / "logs" / "uname"
kld_path = base_hwinfo / "logs" / "kldstat"
cpu_path = base_hwinfo / "logs" / "lscpu"

input_string = "kenv | grep smbios.system.product"
filename_final = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
result = subprocess.run(input_string, capture_output=True, text=True, shell=True)
output_string = result.stdout
filename = re.search('"([^"]*)"', output_string)

if filename:
    filename = filename.group(1)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename_final = f"{filename}_{timestamp}.txt"
    step1 = re.sub(r'[^a-zA-Z0-9_\-.\s]', '_', filename_final)
    filename_final = re.sub(r'\s+', '', step1)

# Gather hardware data from the dumps
device_data = parse_device_data(hw_probe_dump, ifconfig_path, pciconf_path)

# If "html" is provided, generate HTML output
if 'html' in sys.argv:
    html_output = f"test_results/{filename}/index.html"
    generate_html_output(device_data, html_output)
    print(f"Generated HTML report: {html_output}")
else:
    # Otherwise, generate hardware summary in text format
    generate_hardware_summary(ifconfig_path, pciconf_path, hw_probe_dump, filename_final)
    print(f"Generated hardware summary: {filename_final}")
