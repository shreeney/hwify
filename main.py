import sys
from pathlib import Path
import re
from datetime import datetime
import subprocess
import argparse

def get_device(input_file, search_terms):
    if isinstance(search_terms, str):
        search_terms = [search_terms]
    combined_pattern = "|".join([re.escape(term) for term in search_terms])
    subclass_pat = re.compile(rf'subclass\s*=\s*({combined_pattern})', re.IGNORECASE)
    class_pat = re.compile(rf'class\s*=\s*({combined_pattern})', re.IGNORECASE)
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


def get_hw_devices(probe_file, category_name):
    devices = []
    status_pattern = re.compile(r'\b(works|failed|detected|limited|malfunc)\b', re.IGNORECASE)
    try:
        with open(probe_file, 'r') as f:
            for line in f:
                if category_name.lower() in line.lower():
                    status = "unknown"
                    m = status_pattern.search(line)
                    if m:
                        status = m.group(1).lower()
                    devices.append({
                        "raw": line.strip(),
                        "status": status
                    })
    except FileNotFoundError:
        pass
    return devices


#Helper functions for file reading need to take paths
def read_file_content(path, default="Unknown"):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return default


def get_ifconfig_details(input_file):
    pattern = re.compile(r'ssid|media', re.IGNORECASE)
    results = []
    try:
        with open(input_file, 'r') as f:
            for line in f:
                if pattern.search(line):
                    results.append(line.strip())
    except FileNotFoundError:
        return ["Ifconfig file not found."]
    return results if results else ["No Wi-fi info found."]


def generate_hardware_summary(paths, filename, output_filename):
    categories = {
        "Graphics": (("vga", "display"), "graphics card"),
        "Networking": ("network", "network"),
        "Audio": (("hda", "multimedia"), "hda"),
        "Storage": ("mass storage", "storage"),
        "USB Ports": ("usb", "usb"),
        "Bluetooth": ("bluetooth", "bluetooth")
    }

    with open(output_filename, "w") as out:
        out.write("=== FreeBSD Hardware Status Info ===\n\n")
        out.write("Running: ")
        out.write(read_file_content(paths['uname_path'], "Unknown OS"))
        out.write("\n")
        if filename:
            out.write("Hardware: ")
            out.write(filename)
            out.write("\n")

        for label, (pci_key, probe_key) in categories.items():
            pci_blocks = get_device(paths['pciconf_path'], pci_key)
            probe_devices = get_hw_devices(paths['hw_probe_dump'], probe_key)

            out.write(f"- {label}\n")
            if pci_blocks:
                for i, block in enumerate(pci_blocks, 1):
                    hw_status = (
                        probe_devices[i - 1]["status"]
                        if i - 1 < len(probe_devices)
                        else "unknown"
                    )
                    out.write(f"  Device {i} Status: {hw_status.upper()}\n")
                    indented = "    " + block.replace("\n", "\n    ").strip()
                    out.write(f"{indented}\n")
            else:
                out.write("  Status: NOT DETECTED\n")

            out.write("\n" + "-" * 20 + "\n\n")
        out.write("=== FreeBSD Detailed Status Info ==\n\n")

        out.write("Kldstat output:")
        kld_data = read_file_content(paths['kld_path'], "Kldstat file not found.")
        out.write(kld_data)
        out.write("\n" + "=" * 36 + "\n")
        out.write("ifconfig detailed output: ")
        ifconfig_status = get_ifconfig_details(paths['ifconfig_path'])
        out.write("- Active Connection Details: \n")
        for detail in ifconfig_status:
            out.write(f"    {detail}\n")
        out.write("\n")
        out.write("\n")
        out.write("- CPU Info")
        out.write("\n")
        cpu_data = read_file_content(paths['cpu_path'], "CPU info not found.")
        out.write(cpu_data)
        out.write("\n" + "=" * 36 + "\n")



def generate_html_summary(paths):
    categories = {
        "Graphics": (("vga", "display"), "graphics card"),
        "Networking": ("network", "network"),
        "Audio": (("hda", "multimedia"), "hda"),
        "Storage": ("mass storage", "storage"),
        "USB Ports": ("usb", "usb"),
        "Bluetooth": ("bluetooth", "bluetooth")
    }

    html_output = "<tr>\n"

    for label, (pci_key, probe_key) in categories.items():
        pci_blocks = get_device(paths['pciconf_path'], pci_key)
        probe_devices = get_hw_devices(paths['hw_probe_dump'], probe_key)

        cell_content = []
        if pci_blocks:
            for i, block in enumerate(pci_blocks, 1):
                hw_status = (
                    probe_devices[i - 1]["status"]
                    if i - 1 < len(probe_devices)
                    else "unknown"
                )
                vendor_match = re.search(r"vendor\s*=\s*'([^']+)'", block)
                device_match = re.search(r"device\s*=\s*'([^']+)'", block)
                vendor_name = vendor_match.group(1) if vendor_match else "Unknown Vendor"
                device_name = device_match.group(1) if device_match else "Unknown Device"

                status_upper = hw_status.upper()
                cell_content.append(f"{vendor_name} {device_name} ({status_upper})")
        else:
            cell_content.append(f"{label} (NOT DETECTED)")

        html_content = "<br>".join(cell_content)
        html_output += f"  <td>{html_content}</td>\n"

    html_output += "</tr>"

    print(html_output)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate hardware summary for FreeBSD laptop testing. Defaults to creating a text dumpfile.",
        usage="%(prog)s [directory_path] [--html]"
    )

    parser.add_argument("directory_path", nargs="?",
                        default=str(Path.home() / "hwify"),
                        help="Optional path to the hwify directory (defaults to ~/hwify)")

    parser.add_argument("--html", action="store_true",
                        help="Print an HTML table row fragment to stdout instead of generating a dumpfile.")

    args = parser.parse_args()

    tmpdir = Path(args.directory_path)
    base_hwinfo = tmpdir / "hw.info"

    file_paths = {
        'hw_probe_dump': base_hwinfo / "devices",
        'ifconfig_path': base_hwinfo / "logs" / "ifconfig",
        'pciconf_path': base_hwinfo / "logs" / "pciconf",
        'uname_path': base_hwinfo / "logs" / "uname",
        'kld_path': base_hwinfo / "logs" / "kldstat",
        'cpu_path': base_hwinfo / "logs" / "lscpu",
    }

    input_string = "kenv | grep smbios.system.product"
    filename_final = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result = subprocess.run(input_string, capture_output=True, text=True, shell=True)
    output_string = result.stdout
    system_product_name = re.search('"([^"]*)"', output_string)

    if system_product_name:
        system_product_name = system_product_name.group(1)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        temp_filename = f"{system_product_name}_{timestamp}.txt"
        step1 = re.sub(r'[^a-zA-Z0-9_\-.\s]', '_', temp_filename)
        filename_final = re.sub(r'\s+', '', step1)
    else:
        system_product_name = None  # Ensure we pass None if not found

    if args.html:
        generate_html_summary(file_paths)
    else:
        print(f"Generating dump file: {filename_final}")
        generate_hardware_summary(file_paths, system_product_name, filename_final)
