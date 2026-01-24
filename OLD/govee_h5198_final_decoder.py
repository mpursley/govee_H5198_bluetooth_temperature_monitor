import asyncio
from bleak import BleakScanner

def decode(data):
    hex_str = data.hex()
    # Attempt to find 730-750 (73F-75F) or 2200-2400 (22C-24C)
    matches = []
    for i in range(len(data)-1):
        val_le = int.from_bytes(data[i:i+2], 'little')
        val_be = int.from_bytes(data[i:i+2], 'big')
        
        # Check F (scaled by 10)
        if 700 < val_le < 800: matches.append(f"LE@{i}: {val_le/10.0}F")
        if 700 < val_be < 800: matches.append(f"BE@{i}: {val_be/10.0}F")
        
        # Check C (scaled by 100)
        if 2000 < val_le < 2600: matches.append(f"LE@{i}: {val_le/100.0}C ({val_le/100.0*1.8+32:.1f}F)")
        if 2000 < val_be < 2600: matches.append(f"BE@{i}: {val_be/100.0}C ({val_be/100.0*1.8+32:.1f}F)")

    print(f"{hex_str} | {' / '.join(matches)}")

def detection_callback(device, advertisement_data):
    if device.address == "D2:37:31:31:23:2C":
        if advertisement_data.manufacturer_data:
            for company_id, data in advertisement_data.manufacturer_data.items():
                if company_id == 0x2331:
                    decode(data)

async def main():
    print("Monitoring H5198...")
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(60.0)
    await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())
