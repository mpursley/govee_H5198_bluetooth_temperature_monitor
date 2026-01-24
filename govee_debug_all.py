import asyncio
import logging
from bleak import BleakClient, BleakScanner

# TARGET MAC
DEVICE_MAC = "D2:37:31:31:23:2C"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("GoveeDebug")

async def monitor_characteristic(client, char_uuid):
    def callback(sender, data):
        logger.info(f"NOTIFICATION [{char_uuid}]: {data.hex()}")
    
    try:
        await client.start_notify(char_uuid, callback)
        logger.info(f"Subscribed to {char_uuid}")
    except Exception as e:
        logger.error(f"Failed to subscribe to {char_uuid}: {e}")

async def main():
    print(f"--- 🔍 Connecting to {DEVICE_MAC} ---")
    device = await BleakScanner.find_device_by_address(DEVICE_MAC, timeout=20.0)
    if not device:
        print("Device not found.")
        return

    async with BleakClient(device) as client:
        print(f"✅ Connected!")
        
        # Discover all services and characteristics
        for service in client.services:
            print(f"\n[Service] {service.uuid}")
            for char in service.characteristics:
                props = ",".join(char.properties)
                print(f"  └─ [Char] {char.uuid} | Props: [{props}]")
                
                if "notify" in char.properties:
                    await monitor_characteristic(client, char.uuid)
                
                if "read" in char.properties:
                    try:
                        val = await client.read_gatt_char(char.uuid)
                        print(f"     └─ READ: {val.hex()}")
                    except Exception as e:
                        print(f"     └─ READ FAILED: {e}")

        print("\n🚀 Monitoring for 30 seconds... (Watch for updates!)")
        await asyncio.sleep(30.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
