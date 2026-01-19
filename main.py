from collections import defaultdict

HARDWARE_MAP = {
    #"Graphics": ["vga", "display", "nvidia", "intel graphics", "radeon"],
    "Wi-Fi": ["rtw89", "mt7915", "rtw88", "ath", "iwx", "rtwn_usb", "rtwn", "iwlwifi","mt7921","atk10k"],
    #"Audio": ["audio", "sound", "hda", "codec"],
    #"Card Reader": ["card reader", "sdhc", "rtsx"],
    #"Storage": ["sda", "nvme", "ssd"],
    #"Bluetooth": ["bluetooth", "btusb"],
    #"Network": ["ethernet", "rtl8111"]
}


def generate_hardware_summary(input_file, output_file):
    found_details = defaultdict(list)

    with open(input_file, "r") as f:
        for line in f:
            line_lower = line.lower()
            for category, keywords in HARDWARE_MAP.items():
                if any(kw in line_lower for kw in keywords):
                    found_details[category].append(line.strip())

    with open(output_file, "w") as out:
        out.write("=== FREEBSD HARDWARE SUMMARY ===\n\n")

        for category in HARDWARE_MAP:
            is_detected = category in found_details
            out.write(f"{category} Detected: {is_detected}\n")

            if is_detected:
                for detail in found_details[category]:
                    out.write(f"  > {detail}\n")
            else:
                out.write("  > (No matching hardware found)\n")

            out.write("-" * 30 + "\n")

generate_hardware_summary("/root/HW_PROBE/LATEST/hw.info/devices", "freebsd_compat.txt")
