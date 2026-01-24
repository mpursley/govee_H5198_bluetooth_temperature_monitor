import asyncio
import logging
from bleak import BleakScanner

# TARGET DEVICE
TARGET_MAC = "D2:37:31:31:23:2C"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def decode_smart(data):
    hex_str = data.hex()
    
    found_temps = []
    
    # The packet payload usually starts after a 5-byte header: 2c 41 00 02 01
    # We scan 2-byte chunks from offset 5 onwards.
    for i in range(5, len(data) - 1):
        val = int.from_bytes(data[i:i+2], 'little')
        
        # STRATEGY 1: Celsius * 100 (Common for Govee)
        # e.g., 2496 -> 24.96C -> 76.9F
        temp_c = val / 100.0
        temp_f_from_c = (temp_c * 1.8) + 32
        
        # STRATEGY 2: Fahrenheit * 10 (Legacy Govee)
        # e.g., 740 -> 74.0F
        temp_f_direct = val / 10.0
        
        # FILTER: Realistic Cooking/Room Temps (30F to 500F)
        
        # Check Strategy 1
        if 30 < temp_f_from_c < 500:
            # Heuristic: C*100 usually yields specific patterns. 
            # We assume this is the likely candidate if valid.
            found_temps.append(f"Offset {i}: {temp_f_from_c:.1f}°F")
            
        # Check Strategy 2 (only if Strategy 1 didn't claim this value likely)
        elif 30 < temp_f_direct < 500:
            found_temps.append(f"Offset {i}: {temp_f_direct:.1f}°F (F-Mode)")

    if found_temps:
        print(f"📦 Packet: {hex_str}")
        print(f"   🎯 Decoded: { '  |  '.join(found_temps) }")
        print("-" * 40)

def detection_callback(device, advertisement_data):
    if device.address == TARGET_MAC:
        # Check Manufacturer Data (ID 0x2331 seems to be the one)
        if advertisement_data.manufacturer_data:
            for company_id, data in advertisement_data.manufacturer_data.items():
                if company_id == 0x2331:
                    decode_smart(data)

async def main():
    print(f"--- 🍖 Monitoring Govee H5198 ({TARGET_MAC}) ---")
    print("Scanning for broadcast data... (Press Ctrl+C to stop)")
    
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    
    try:
        # Run forever until interrupted
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
