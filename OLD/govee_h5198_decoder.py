import asyncio
from bleak import BleakScanner

def decode_govee_h5198(data):
    # data is a bytes object
    # Based on observation: 2c 41 00 02 01 e4 [PROBE1_LOW] [PROBE1_HIGH] ...
    # Wait, in the second run it was: 2c 41 00 02 01 e4 02 80 ff ff ...
    # Let's look at the offsets.
    # 00: 2c
    # 01: 41
    # 02: 00
    # 03: 02
    # 04: 01
    # 05: e4
    # 06: 02  <-- Probe 1 High?
    # 07: 80  <-- Probe 1 Low?
    # Wait, 0x0280 = 640. 64.0F? 
    # Let's try 0x8002? No.
    
    # Let's look at the first run again:
    # 05: e4
    # 06: 41
    # 07: c0
    # 0x41c0 = 16832.
    # 0xc041 = 49217.
    
    # What if it's 3 bytes per probe?
    # Or what if the first run had a different value?
    
    # Let's just print the raw bytes and look for patterns.
    hex_str = data.hex()
    print(f"RAW: {hex_str}")
    
    # If 0x02e4 = 740 was the temp... where was it in the raw?
    # Run 2: 2c 41 00 02 01 e4 02 80 ...
    # 02 e4 is NOT there. e4 02 is there at index 5 and 6!
    # Index 5: e4, Index 6: 02.
    # 0x02e4 = 740. YES!
    
    # So:
    # Probe 1: data[5:7] (Little Endian)
    # Probe 2: data[7:9] ?
    # Let's check Run 2 again: data[7:9] is 80 ff. 0xff80. 
    # Run 1: data[7:9] was c0 08. 0x08c0 = 2240. 224.0F?
    
    p1_raw = int.from_bytes(data[5:7], 'little')
    p2_raw = int.from_bytes(data[7:9], 'little')
    p3_raw = int.from_bytes(data[9:11], 'little')
    p4_raw = int.from_bytes(data[11:13], 'little')
    
    print(f"  Probe 1: {p1_raw/10.0:.1f} F" if p1_raw != 0xffff else "  Probe 1: --")
    print(f"  Probe 2: {p2_raw/10.0:.1f} F" if p2_raw != 0xffff else "  Probe 2: --")
    print(f"  Probe 3: {p3_raw/10.0:.1f} F" if p3_raw != 0xffff else "  Probe 3: --")
    print(f"  Probe 4: {p4_raw/10.0:.1f} F" if p4_raw != 0xffff else "  Probe 4: --")

def detection_callback(device, advertisement_data):
    if device.address == "D2:37:31:31:23:2C":
        if advertisement_data.manufacturer_data:
            for company_id, data in advertisement_data.manufacturer_data.items():
                if company_id == 0x2331:
                    decode_govee_h5198(data)

async def main():
    print("Monitoring H5198 (D2:37:31:31:23:2C)...")
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(30.0)
    await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())
