import sys
import re
import os

def parse_hardware_dump(dump_text):
    """
    Parses hardware dump text into a dictionary of hardware categories and details.
    """
    hardware_data = {}
    current_category = None

    lines = dump_text.strip().split('\n')
    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Check for category headers (lines starting with -+ or a single word followed by :)
        # Using a more robust regex for various header formats
        category_match = re.match(r'^(-+\s)?([\w\s]+?):', line)
        if category_match:
            # Extract category name, convert to title case for consistency
            current_category = category_match.group(2).strip().title()
            # Normalize common category names
            if current_category == 'Usb Ports':
                current_category = 'USB Ports'
            hardware_data[current_category] = {}
        elif current_category:
            # Extract key-value pairs within a category
            kv_match = re.match(r'(\w+\s?\w*)\s*[=:](.*)', line)
            if kv_match:
                key = kv_match.group(1).strip().lower()
                value = kv_match.group(2).strip()
                hardware_data[current_category][key] = value
            elif 'Status:' in line or 'Status :' in line:
                # Special handling for "Device X Status: VALUE" lines
                status_match = re.search(r'Status\s*:\s*(.*)', line)
                if status_match:
                    # Append status to the current device if possible
                    last_device_key = sorted(hardware_data[current_category].keys())[-1] if hardware_data[current_category] else None
                    if last_device_key and 'status' not in hardware_data[current_category][last_device_key].lower():
                         hardware_data[current_category][last_device_key] += f" Status: {status_match.group(1).strip()}"

    return hardware_data

def generate_html_row(hardware_data):
    """
    Generates an HTML table row (<tr>) from the parsed hardware data.
    """
    html_output = "<tr>\n"

    # The first cell is the overall "Hardware name"
    system_info = hardware_data.get('System', {}).get('hardware', 'Unknown System')
    html_output += f"    <td>{system_info}</td>\n"

    # Define the preferred order, including Bluetooth.
    # We dynamically check the keys present in hardware_data
    preferred_order = ['Graphics', 'Networking', 'Audio', 'Storage', 'USB Ports', 'Bluetooth']
    ordered_categories = [cat for cat in preferred_order if cat in hardware_data or cat in preferred_order]

    for category in ordered_categories:
        cell_content = "N/A"
        if category in hardware_data:
            devices = hardware_data[category]
            if devices:
                # Get the most descriptive field for the device name
                device_name_key = next((k for k in ['device', 'vendor'] if k in devices), None)
                first_device_name = devices.get(device_name_key, 'Unknown Device')
                # Find the status among all keys
                first_device_status = next((v for k, v in devices.items() if 'status' in k.lower()), 'N/A')
                cell_content = f"{first_device_name} ({first_device_status.strip()})"

        html_output += f"    <td>{cell_content}</td>\n"

    html_output += "</tr>"
    return html_output

if __name__ == "__main__":
    hardware_dump_text = ""
    file_path = None

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                hardware_dump_text = f.read()
        else:
            print(f"Error: File not found at {file_path}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        hardware_dump_text = sys.stdin.read()


    parsed_data = parse_hardware_dump(hardware_dump_text)
    html_row = generate_html_row(parsed_data)
    print(html_row)
