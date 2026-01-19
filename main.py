from collections import defaultdict

HARDWARE_MAP = {
    "Graphics": ["vga", "display", "nvidia", "intel graphics", "radeon"],
    "Wi-Fi": ["wireless", "wlan", "802.11", "iwlwifi", "ath9k"],
    "Audio": ["audio", "sound", "hda", "codec"],
    "Card Reader": ["card reader", "sdhc", "rtsx"],
    "Storage": ["sda", "nvme", "ssd"],
    "Bluetooth": ["bluetooth", "btusb"],
    "Network": ["ethernet", "rtl8111"]
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

generate_hardware_summary("/root/HW_PROBE/LATEST/hw.info/devices", "freebsd_compat.txt")
