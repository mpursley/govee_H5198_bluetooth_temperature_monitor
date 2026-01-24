import asyncio
import logging
from bleak import BleakClient, BleakScanner

# CONFIGURATION
# The new strong "Unknown" candidate
DEVICE_MAC = "4C:B2:CD:F4:47:E8" 

logging.basicConfig(level=logging.INFO)

async def main():
    print(f"--- CONNECTING TO CANDIDATE: {DEVICE_MAC} ---")
    print("1. Scanning...")
    
    device = await BleakScanner.find_device_by_address(DEVICE_MAC, timeout=20.0)
    if not device:
        print("   [!] Device not found. WAKE IT UP (press a button) and try again.")
        return

    print(f"2. Connecting to {device.name or DEVICE_MAC}...")
    
    try:
        async with BleakClient(device, timeout=30.0) as client:
            print(f"   [+] Connected! (Paired: {client.is_connected})")
            
            print("\n3. Reading Data (Looking for ~73°F / ~22.7°C)...")
            for service in client.services:
                for char in service.characteristics:
                    if "read" in char.properties:
                        try:
                            val = await client.read_gatt_char(char.uuid)
                            hex_val = val.hex()
                            
                            # Simple Little Endian Decode
                            # Many Govee devices pack temps as 2 bytes: 2275 -> 22.75°C
                            if len(val) >= 2:
                                val_int = int.from_bytes(val, 'little')
                                temp_c = val_int / 100.0
                                temp_f = (temp_c * 1.8) + 32
                                
                                # Highlight if it looks like a valid temp
                                marker = ""
                                if 60 < temp_f < 90: 
                                    marker = " <--- PROBABLE MATCH"
                                
                                print(f"   [UUID] {char.uuid}")
                                print(f"     └─ HEX: {hex_val}")
                                print(f"     └─ INT: {val_int}  => {temp_c:.2f}°C  |  {temp_f:.2f}°F{marker}")

                        except Exception as e:
                            pass 
                            
    except Exception as e:
        print(f"\n[!] Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())