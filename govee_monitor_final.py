import asyncio
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
        
        if updated:
            print(f"\r[Govee H5198] P1: {probe_data[1]:>7} | P2: {probe_data[2]:>7} | P3: {probe_data[3]:>7} | P4: {probe_data[4]:>7}", end="", flush=True)

async def main():
    print(f"--- Monitoring Govee H5198 ({TARGET_MAC}) ---")
    print("Aggregate view of all 4 probes:")
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    try:
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
