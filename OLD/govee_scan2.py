import asyncio
import logging
from bleak import BleakClient, BleakScanner

# TARGET MAC (Your confirmed H5198)
DEVICE_MAC = "D2:37:31:31:23:2C"

# UUIDS
NOTIFY_UUID = "00010203-0405-0607-0809-0a0b0c0d2b10"
CONTROL_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"

# COMMAND LIST (The "Keys")
COMMANDS = [
    # 1. Standard Handshake WITH Checksum (33^11=22)
    bytearray([0x33, 0x11, 0x00, 0x00, 0x00, 0x22]),
    
    # 2. Standard Handshake (No Checksum) - Just in case
    bytearray([0x33, 0x11, 0x00, 0x00, 0x00, 0x00]),
    
    # 3. Alternative Handshake (Common on WiFi models)
    bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x01]),
]

logging.basicConfig(level=logging.INFO)

def notification_handler(sender, data):
    hex_str = data.hex()
    print(f"   [RX] {hex_str} (Len: {len(data)})")
    
    # DATA DECODER
    # Govee H5198 packets are usually 20 bytes.
    # The temperature is often at offset 10, 11, or 12.
    if len(data) > 8:
        try:
            # Decode the whole packet into 2-byte chunks to find the temp
            chunks = []
            for i in range(0, len(data)-1):
                val = int.from_bytes(data[i:i+2], 'little')
                chunks.append(f"{val}")
                
                # Check if this chunk looks like 73F (approx 2200-2300 raw int)
                temp_c = val / 100.0
                temp_f = (temp_c * 1.8) + 32
                
                if 70 < temp_f < 76:
                    print(f"      ★ FOUND TEMP @ Byte {i}: {temp_f:.2f}°F (Int: {val})")
                    
        except:
            pass

async def main():
    print(f"--- CONNECTING TO {DEVICE_MAC} ---")
    device = await BleakScanner.find_device_by_address(DEVICE_MAC, timeout=20.0)
    
    if not device:
        print("[!] Device not found.")
        return

    async with BleakClient(device) as client:
        print(f"✅ CONNECTED!")
        
        print(f"Subscribing to {NOTIFY_UUID}...")
        await client.start_notify(NOTIFY_UUID, notification_handler)
        
        # Try commands one by one
        for i, cmd in enumerate(COMMANDS):
            print(f"\n🔑 Trying Key #{i+1}: {cmd.hex()}")
            await client.write_gatt_char(CONTROL_UUID, cmd)
            
            print("   Listening for 5 seconds...")
            await asyncio.sleep(5.0)
            
        print("\n--- Done ---")

if __name__ == "__main__":
    asyncio.run(main())