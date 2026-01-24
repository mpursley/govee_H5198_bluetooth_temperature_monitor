import asyncio
from bleak import BleakScanner

def detection_callback(device, advertisement_data):
    if device.address == "D2:37:31:31:23:2C":
        print(f"\n--- {device.address} ---")
        print(f"RSSI: {advertisement_data.rssi}")
        if advertisement_data.manufacturer_data:
            for company_id, data in advertisement_data.manufacturer_data.items():
                print(f"  Mfg Data [ID {company_id:#06x}]: {data.hex()}")
        if advertisement_data.service_data:
            for service_uuid, data in advertisement_data.service_data.items():
                print(f"  Service Data [UUID {service_uuid}]: {data.hex()}")
        if advertisement_data.service_uuids:
            print(f"  Service UUIDs: {advertisement_data.service_uuids}")

async def main():
    print("Scanning for D2:37:31:31:23:2C...")
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(10.0)
    await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())

