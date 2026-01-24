import asyncio
from bleak import BleakScanner

# CONFIGURATION
TARGET_NAME_PART = "H5198"
DEBUG = True  # Set to True to see ALL devices found

def decode_ibeacon(mfg_data):
    """
    H5198 often encodes temp in the Major/Minor fields of the iBeacon payload.
    Standard iBeacon payload (after company ID 0x004c and type 0x02, length 0x15):
    [UUID (16 bytes)] [Major (2 bytes)] [Minor (2 bytes)] [TxPower (1 byte)]
    """
    if 76 in mfg_data: # 0x004c is Apple
        payload = mfg_data[76]
        if len(payload) >= 23 and payload[0] == 0x02 and payload[1] == 0x15:
            major = int.from_bytes(payload[18:20], byteorder='big')
            minor = int.from_bytes(payload[20:22], byteorder='big')
            
            print(f"    [iBeacon] Major: {major}, Minor: {minor}")
            print(f"    [Potential Decode] Probe 1: {major / 10.0}°C (?)")
            return

    for company_id, data in mfg_data.items():
        print(f"    [Raw Mfg Data] ID: {company_id:#06x} Hex: {data.hex()}")

def detection_callback(device, advertisement_data):
    # Get a safe name string even if device.name is None
    dev_name = device.name or "Unknown"
    
    # DEBUG: Print everything to find the correct name
    if DEBUG:
        print(f"[DEBUG] Found: {dev_name:<20} | MAC: {device.address} | RSSI: {advertisement_data.rssi}")

    # Check for target
    if device.name and TARGET_NAME_PART in device.name:
        print(f"\n>>> TARGET MATCH: {device.name} (MAC: {device.address})")
        
        if advertisement_data.manufacturer_data:
            decode_ibeacon(advertisement_data.manufacturer_data)
        else:
            print("    No manufacturer data found in this packet.")

async def main():
    print(f"Scanning for devices (Target: '{TARGET_NAME_PART}')...")
    print(f"Debug Mode: {'ON' if DEBUG else 'OFF'}\n")
    
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(20.0)
    await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())