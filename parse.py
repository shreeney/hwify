import json
import re
import argparse
from pathlib import Path

# logic for taking in cmd line params
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
    data = {}  # empty dict
    current_section = None
    current_device = None

    hardware_name_re = re.compile(r"Hardware:\s*(.*)")

    device_header_re = re.compile(r"Device (\d+) Status: (\w+)")
    key_value_re = re.compile(r"(\w+)\s*=\s*'?(.*?)'?$")

    with open(path) as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            m = hardware_name_re.match(line)
            if m:
                data['hardware_name'] = m.group(1)
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


def generate_html_table(data):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Laptop Compatibility Table</title>
      <link rel="stylesheet" href="styles.css">
    </head>
    <body>
      <h1>Laptop Compatibility Information</h1>
      <table id="compatibility-table">
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
        <td>{data['hardware_name']}</td>
    """

    categories = ["Graphics", "Networking", "Audio", "Storage", "USB Ports"]
    for category in categories:
        html_content += "<td>"
        if category in data:
            devices = data[category]
            for device in devices:
                device_info = f"{device['device']} ({device['status']})<br>"
                device_info += f"Vendor: {device['vendor']}<br>"
                device_info += f"Identifier: {device['identifier']}<br>"
                device_info += f"Subvendor: {device['subvendor']}<br>"
                device_info += f"Subdevice: {device['subdevice']}<br><hr>"
                html_content += device_info
        html_content += "</td>"

    html_content += """
        </tr>
      </tbody>
    </table>
    </body>
    </html>
    """

    return html_content


# main function
def main():
    parsed = parse_hardware_status(file_path)

    with open("hardware.json", "w") as file:
        json.dump(parsed, file, indent=2)

    html_content = generate_html_table(parsed)

    with open("index.html", "w") as file:
        file.write(html_content)


if __name__ == "__main__":
    main()
