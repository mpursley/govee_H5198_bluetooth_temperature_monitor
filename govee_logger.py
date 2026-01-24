import asyncio
import datetime
from bleak import BleakScanner

TARGET_MAC = "D2:37:31:31:23:2C"

# Global state to store the latest values for all 4 probes
probe_data = {
    1: "--",
    2: "--",
    3: "--",
    4: "--"
}

def decode_temp(b):
    if b == b'\xff\xff' or b == b'\x00\x00':
        return None
    val = int.from_bytes(b, 'big')
    temp_c = val / 100.0
    temp_f = (temp_c * 1.8) + 32
    return f"{temp_f:.1f}°F"

def detection_callback(device, advertisement_data):
    if device.address == TARGET_MAC:
        mdata = advertisement_data.manufacturer_data.get(0x2331)
        if not mdata or len(mdata) < 16:
            return

        pkt_type = mdata[6]

        if pkt_type == 0xc1:
            p1 = decode_temp(mdata[8:10])
            p2 = decode_temp(mdata[14:16])
            if p1: probe_data[1] = p1
            if p2: probe_data[2] = p2
        elif pkt_type == 0xc2:
            p3 = decode_temp(mdata[8:10])
            p4 = decode_temp(mdata[14:16])
            if p3: probe_data[3] = p3
            if p4: probe_data[4] = p4

async def logger_loop():
    header = f"{'Time':<10} | {'P1':>8} | {'P2':>8} | {'P3':>8} | {'P4':>8}"
    print(header)
    print("-" * 55)

    with open("temperature_log.txt", "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write("-" * 55 + "\n")
    
    start_time = datetime.datetime.now()
    duration = datetime.timedelta(minutes=2)
    
    while datetime.datetime.now() - start_time < duration:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"{now:<10} | {probe_data[1]:>8} | {probe_data[2]:>8} | {probe_data[3]:>8} | {probe_data[4]:>8}"
        print(line)
        
        with open("temperature_log.txt", "a", encoding="utf-8") as f:
            f.write(line + "\n")
            
        await asyncio.sleep(5)
    
    print("\n--- 2 minutes complete. Stopping... ---")

async def main():
    print(f"--- 🍖 Govee H5198 Logger ({TARGET_MAC}) ---")
    print("Logging every 5 seconds. Press Ctrl+C to stop.\n")
    
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    
    try:
        await logger_loop()
    except asyncio.CancelledError:
        pass
    finally:
        await scanner.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping...")
