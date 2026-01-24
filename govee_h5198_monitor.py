import asyncio
import logging
from bleak import BleakScanner

# TARGET DEVICE
TARGET_MAC = "D2:37:31:31:23:2C"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def decode_temp(val_bytes):
    if val_bytes == b'\xff\xff':
        return "--"
    
    val_int = int.from_bytes(val_bytes, 'big')
    temp_c = val_int / 100.0
    temp_f = (temp_c * 1.8) + 32
    return f"{temp_f:.1f}°F"

def decode_packet(data):
    hex_str = data.hex()
    
    # Header check (loose)
    # 2c 41 00 02 01 e4 ...
    if len(data) < 16:
        return

    # Packet Type (byte 6)
    pkt_type = data[6] # c1 or c2? 
    
    # Slot 1: Bytes 8-9
    s1 = decode_temp(data[8:10])
    
    # Slot 2: Bytes 10-11
    s2 = decode_temp(data[10:12])
    
    # Slot 3: Bytes 12-13
    s3 = decode_temp(data[12:14])
    
    # Slot 4: Bytes 14-15
    s4 = decode_temp(data[14:16])
    
    print(f"[{hex_str[12:14]}] Type {pkt_type:02x} | Slot 1: {s1} | Slot 2: {s2} | Slot 3: {s3} | Slot 4: {s4}")

def detection_callback(device, advertisement_data):
    if device.address == TARGET_MAC:
        if advertisement_data.manufacturer_data:
            for company_id, data in advertisement_data.manufacturer_data.items():
                if company_id == 0x2331:
                    decode_packet(data)

async def main():
    print(f"--- 🍖 Govee Monitor {TARGET_MAC} ---")
    print("Slot mapping is TBD. Look for the value > 80°F.")
    
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    
    try:
        while True:
            await asyncio.sleep(1.0)
    except asyncio.CancelledError:
        pass
    finally:
        await scanner.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping...")
