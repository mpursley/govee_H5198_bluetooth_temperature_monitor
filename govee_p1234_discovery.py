import asyncio
from bleak import BleakScanner

TARGET_MAC = "D2:37:31:31:23:2C"

def decode_temp_c100(b):
    if b == b'\xff\xff' or b == b'\x00\x00':
        return None
    val = int.from_bytes(b, 'big')
    temp_c = val / 100.0
    temp_f = (temp_c * 1.8) + 32
    return round(temp_f, 1)

def detection_callback(device, advertisement_data):
    if device.address == TARGET_MAC:
        mdata = advertisement_data.manufacturer_data.get(0x2331)
        if not mdata or len(mdata) < 16:
            return

        pkt_type = mdata[6]
        # Data slots at offsets 8, 10, 12, 14
        s1 = decode_temp_c100(mdata[8:10])
        s2 = decode_temp_c100(mdata[10:12])
        s3 = decode_temp_c100(mdata[12:14])
        s4 = decode_temp_c100(mdata[14:16])
        
        print(f"Type {pkt_type:02x} | S1: {s1 if s1 else '--':>5} | S2: {s2 if s2 else '--':>5} | S3: {s3 if s3 else '--':>5} | S4: {s4 if s4 else '--':>5} | Raw: {mdata.hex()}")

async def main():
    print(f"Monitoring {TARGET_MAC}...")
    print("Target: P1=108, P2=75, P3=75, P4=77")
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(30.0)
    await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())
