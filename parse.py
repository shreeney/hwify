import re
import sys


# Function to parse the hardware information
def parse_hardware_status(file_path):
    with open(file_path, 'r') as file:
        hardware_info = file.read()

    # Regular expressions to match device sections
    section_pattern = re.compile(r"-\s([A-Za-z]+)")
    device_pattern = re.compile(r"Device\s(\d+)\sStatus:\s(\w+).+device\s=\s'([^']+)'")
    model_pattern = re.compile(r"Hardware:\s([A-Za-z0-9\s\(\)]+)")

    hardware_data = {}
    current_section = None
    current_model = None

    # Find the laptop model
    model_match = model_pattern.search(hardware_info)
    if model_match:
        current_model = model_match.group(1)
        print(f"Found model: {current_model}")  # Debug: Check the found model
    else:
        print("Model not found in the file.")
        return

    # Initialize hardware categories
    hardware_data[current_model] = {
        'Graphics': [],
        'Networking': [],
        'Audio': [],
        'Storage': [],
        'USB Ports': [],
        'Bluetooth': []
    }

    # Process each line to extract the device details
    for line in hardware_info.splitlines():
        # Match section headers (like Graphics, Networking, etc.)
        section_match = section_pattern.match(line)
        if section_match:
            current_section = section_match.group(1)
            print(f"Found section: {current_section}")  # Debug: Check section name

        # Match device details (device name and status)
        device_match = device_pattern.match(line)
        if device_match and current_section:
            device_num = device_match.group(1)
            status = device_match.group(2)
            device_name = device_match.group(3)

            # Debug: Check if devices are being found
            print(f"Found device: {device_name} Status: {status} in section: {current_section}")

            # Add the device to the correct category in the hardware data
            if current_section in hardware_data[current_model]:
                hardware_data[current_model][current_section].append((device_name, status))

    # Generate HTML table
    html_output = '<table border="1" cellpadding="5" cellspacing="0">'
    html_output += '<tr><th>Model</th><th>Graphics</th><th>Networking</th><th>Audio</th><th>Storage</th><th>USB Ports</th><th>Bluetooth</th></tr>'

    # Prepare the data for each section in the table row
    row = f'<tr><td>{current_model}</td>'

    # For each section (column), insert the devices and their status
    for hw_section in ['Graphics', 'Networking', 'Audio', 'Storage', 'USB Ports', 'Bluetooth']:
        row += f'<td>'
        # For each device in the section, add the name and status
        if hw_section in hardware_data[current_model]:
            if hardware_data[current_model][hw_section]:  # Check if there are any devices
                for device in hardware_data[current_model][hw_section]:
                    row += f'{device[0]} ({device[1]})<br>'
            else:
                row += 'No devices found<br>'  # Debug: Handle empty sections
        row += '</td>'

    row += '</tr>'
    html_output += row

    html_output += '</table>'

    # Print the HTML output to the standard output
    print(html_output)


# Main script execution
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    parse_hardware_status(file_path)
