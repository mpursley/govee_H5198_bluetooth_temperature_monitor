import asyncio
from bleak import BleakScanner

def detection_callback(device, advertisement_data):
    if device.address == "D2:37:31:31:23:2C":
        if advertisement_data.manufacturer_data:
            for company_id, data in advertisement_data.manufacturer_data.items():
                print(f"{data.hex()}")

async def main():
    print("Monitoring D2:37:31:31:23:2C for 20 seconds...")
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(20.0)
    await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())
