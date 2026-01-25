import asyncio
from bleak import BleakScanner

TARGET_DEVICE_MAC = None
SYNC_COMPLETE = False

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

    if device.address == TARGET_DEVICE_MAC:
        mdata = advertisement_data.manufacturer_data[0x2331]
        if len(mdata) < 16:
            return

        pkt_type = mdata[6]
        updated = False

        if pkt_type == 0xc1:
            p1 = decode_temp(mdata[8:10])
            p2 = decode_temp(mdata[14:16])
            if p1: probe_data[1] = p1
            if p2: probe_data[2] = p2
            updated = True
        elif pkt_type == 0xc2:
            p3 = decode_temp(mdata[8:10])
            p4 = decode_temp(mdata[14:16])
            if p3: probe_data[3] = p3
            if p4: probe_data[4] = p4
            updated = True
        
        # Only print from callback if we are DONE syncing.
        # During sync, the main loop handles printing.
        if updated and SYNC_COMPLETE:
            print(f"\r[Govee H5198] P1: {probe_data[1]:>7} | P2: {probe_data[2]:>7} | P3: {probe_data[3]:>7} | P4: {probe_data[4]:>7}", end="", flush=True)

async def main():
    global SYNC_COMPLETE
    print(f"--- Monitoring Govee H5198 (Auto-Discovery) ---")
    print("Aggregate view of all 4 probes:")
    print("Searching for device and waiting for all probes to report...")
    
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    
    try:
        # Syncing Phase: Wait for all 4 probes or 60 second timeout
        start_wait = asyncio.get_event_loop().time()
        
        while any(v == "--" for v in probe_data.values()):
            # Show current values filling in
            status = f"\r[Syncing...] P1: {probe_data[1]:>7} | P2: {probe_data[2]:>7} | P3: {probe_data[3]:>7} | P4: {probe_data[4]:>7}"
            print(status, end="", flush=True)
            
            if asyncio.get_event_loop().time() - start_wait > 60:
                print("\n[!] Sync timeout (60s). Some probes may be unplugged.")
                break
            await asyncio.sleep(0.5)
        
        # Enable callback printing
        SYNC_COMPLETE = True
        print("\n[!] Initial sync complete. Starting live monitor...\n")
        
        # The loop just keeps the script alive; printing is now handled by the callback
        while True:
            await asyncio.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        await scanner.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping...")
