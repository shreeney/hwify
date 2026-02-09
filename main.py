import sys
from pathlib import Path
import re
from datetime import datetime
import subprocess


def generate_html_report(dump_file_path, output_html):
    # Make sure the file exists
    if not Path(dump_file_path).exists():
        print(f"Error: The file '{dump_file_path}' does not exist.")
        sys.exit(1)

    categories = {
        "Graphics": (("vga", "display"), "graphics card"),
        "Networking": ("network", "network"),
        "Audio": (("hda", "multimedia"), "hda"),
        "Storage": ("mass storage", "storage"),
        "USB Ports": ("usb", "usb"),
        "Bluetooth": ("bluetooth", "bluetooth")
    }

    # Start HTML content (Basic layout with a header and a table)
    html_content = f"""
    <html>
    <head>
        <title>Laptop Compatibility Report</title>
    </head>
    <body>
        <h1>Laptop Compatibility Report</h1>
        <h2>Laptop: {Path(dump_file_path).name}</h2>
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Device</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
    """

    with open(dump_file_path, "r") as file:
        dump_content = file.read()

    # Parse and generate table rows for each category
    for label, (pci_key, probe_key) in categories.items():
        devices = get_device_info_for_category(dump_content, pci_key, probe_key)

        if devices:
            for i, (status, block) in enumerate(devices, 1):
                indented_block = block.replace("\n", "<br>")
                html_content += f"""
                <tr>
                    <td>{label}</td>
                    <td>Device {i}</td>
                    <td>{status.upper()}</td>
                    <td>{indented_block}</td>
                </tr>
                """
        else:
            html_content += f"""
            <tr>
                <td>{label}</td>
                <td colspan="3">Status: NOT DETECTED</td>
            </tr>
            """

    # Close HTML structure
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    # Write the HTML content to the output file
    with open(output_html, 'w') as out_html:
        out_html.write(html_content)

    print(f"HTML report saved to {output_html}")


# Function to extract device information for a given category from the dump content
def get_device_info_for_category(dump_content, pci_key, probe_key):
    results = []

    # Categories are searched for in the content (pci_key is for finding PCI devices, probe_key is for hardware probe data)
    search_pattern = re.compile(rf"(-\s*{pci_key}|{probe_key})(.*?)(?=\n\s*-|\Z)", re.DOTALL | re.IGNORECASE)
    matches = search_pattern.findall(dump_content)

    for match in matches:
        label, block = match
        status = "unknown"

        # Check if we can find a status (works, detected, etc.) within the block
        status_pattern = re.compile(r'\b(works|failed|detected|limited|malfunc)\b', re.IGNORECASE)
        status_match = status_pattern.search(block)
        if status_match:
            status = status_match.group(1).lower()

        results.append((status, block.strip()))

    return results


# Function to generate hardware summary (unchanged)
def generate_hardware_summary(ifconfig, pciconf, hw_probe, output):
    categories = {
        # multiple aliases for devices are in pciconf, so have some logic to handle it
        "Graphics": (("vga", "display"), "graphics card"),
        "Networking": ("network", "network"),
        "Audio": (("hda", "multimedia"), "hda"),
        "Storage": ("mass storage", "storage"),
        "USB Ports": ("usb", "usb"),
        "Bluetooth": ("bluetooth", "bluetooth")
    }

    with open(output, "w") as out:
        out.write("=== FreeBSD Hardware Status Info ===\n\n")
        out.write("Running: ")
        out.write(get_uname_details())
        out.write("\n")
        out.write("Hardware: ")
        out.write(filename)
        out.write("\n")
        for label, (pci_key, probe_key) in categories.items():

            pci_blocks = get_device(pciconf, pci_key)
            probe_devices = get_hw_devices(hw_probe, probe_key)

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
        kld_data = get_kldstat()
        out.write(kld_data)
        out.write("\n" + "=" * 36 + "\n")
        out.write("ifconfig detailed output: ")
        ifconfig_status = get_ifconfig_details(ifconfig)
        out.write("- Active Connection Details: \n")
        for detail in ifconfig_status:
            out.write(f"    {detail}\n")
        out.write("\n")
        out.write("\n")
        out.write("- CPU Info")
        out.write("\n")
        cpu_data = get_cpuinfo()
        out.write(cpu_data)
        out.write("\n" + "=" * 36 + "\n")


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


def get_uname_details():
    uname_file = open(uname_path, "r")
    content = uname_file.read()
    return content


def get_kldstat():
    kld_file = open(kld_path, "r")
    content = kld_file.read()
    return content


def get_cpuinfo():
    cpu_file = open(cpu_path, "r")
    content = cpu_file.read()
    return content


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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <dump_file_path> [html <output_html_path>]")
        sys.exit(1)

    # Default directory for hardware info files
    tmpdir = Path(sys.argv[1])

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

    generate_hardware_summary(ifconfig_path, pciconf_path, hw_probe_dump, filename_final)

    if len(sys.argv) == 4 and sys.argv[2] == 'html':
        dump_file_path = filename_final
        output_html_path = sys.argv[3]
        generate_html_report(dump_file_path, output_html_path)
