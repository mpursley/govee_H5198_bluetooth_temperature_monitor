import asyncio
import datetime
import os
import sys
from bleak import BleakScanner

# We will auto-discover the device.
TARGET_DEVICE_MAC = None

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
    global TARGET_DEVICE_MAC
    
    # 1. Check if this is a Govee H5198 device (Manufacturer ID 0x2331)
    if 0x2331 not in advertisement_data.manufacturer_data:
        return

    # 2. If we haven't found our target yet, lock onto this one.
    if TARGET_DEVICE_MAC is None:
        TARGET_DEVICE_MAC = device.address
        print(f"\n[+] Auto-discovered Govee Device: {TARGET_DEVICE_MAC}")

    # 3. Only process data from the locked target
    if device.address == TARGET_DEVICE_MAC:
        mdata = advertisement_data.manufacturer_data[0x2331]
        if len(mdata) < 16:
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

async def logger_loop(duration_minutes=None):
    # Ensure log directory exists
    log_dir = "temperature_logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    txt_filename = os.path.join(log_dir, f"temperature_log_{timestamp}.txt")
    csv_filename = os.path.join(log_dir, f"temperature_log_{timestamp}.csv")

    # Console & TXT Header
    header = f"{'Time':<10} | {'P1':>8} | {'P2':>8} | {'P3':>8} | {'P4':>8}"
    print(header)
    print("-" * 55)
    print(f"Logging to: {txt_filename} and {csv_filename}")
    if duration_minutes:
        print(f"Duration: {duration_minutes} minutes")
    else:
        print("Duration: Indefinite (Press Ctrl+C to stop)")
    print("-" * 55)

    # Initialize TXT file
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write("-" * 55 + "\n")

    # Initialize CSV file
    with open(csv_filename, "w", encoding="utf-8") as f:
        f.write("Time,P1,P2,P3,P4\n")
    
    start_time = datetime.datetime.now()
    if duration_minutes:
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)
    else:
        end_time = None
    
    while True:
        # Check duration if not indefinite
        if end_time and datetime.datetime.now() >= end_time:
            break

        now = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Formatted line for Console & TXT
        txt_line = f"{now:<10} | {probe_data[1]:>8} | {probe_data[2]:>8} | {probe_data[3]:>8} | {probe_data[4]:>8}"
        print(txt_line)
        
        # Write to TXT
        with open(txt_filename, "a", encoding="utf-8") as f:
            f.write(txt_line + "\n")

        # Write to CSV
        csv_line = f"{now},{probe_data[1]},{probe_data[2]},{probe_data[3]},{probe_data[4]}"
        with open(csv_filename, "a", encoding="utf-8") as f:
            f.write(csv_line + "\n")
            
        await asyncio.sleep(5)
    
    print(f"\n--- {duration_minutes if duration_minutes else 'Indefinite'} minutes complete. Stopping... ---")

async def main():
    # Parse CLI args
    duration = None
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            print("Usage: python govee_logger.py [minutes]")
            print("  If [minutes] is omitted, runs indefinitely.")
            return

    print(f"--- 🍖 Govee H5198 Logger (Auto-Discovery Mode) ---")
    print("Logging every 5 seconds. Press Ctrl+C to stop.\n")
    
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    
    try:
        # Syncing Phase: Wait for all probes before starting the log
        print("Waiting for all probes to report before starting log...")
        start_wait = asyncio.get_event_loop().time()
        while any(v == "--" for v in probe_data.values()):
            found = [f"P{i}" for i, v in probe_data.items() if v != "--"]
            print(f"\r[Syncing] Probes found: {', '.join(found) if found else 'None'}", end="", flush=True)
            
            if asyncio.get_event_loop().time() - start_wait > 60:
                print("\n[!] Sync timeout. Starting log with available probes.")
                break
            await asyncio.sleep(1.0)
        
        print("\n[!] Sync complete. Starting log loop...\n")
        await logger_loop(duration)
    except asyncio.CancelledError:
        pass
    finally:
        await scanner.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping...")
