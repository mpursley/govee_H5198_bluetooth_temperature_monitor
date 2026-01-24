import asyncio
import logging
from bleak import BleakClient, BleakScanner

# TARGET MAC
DEVICE_MAC = "D2:37:31:31:23:2C"

# UUIDS
CONTROL_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"
NOTIFY_UUID = "00010203-0405-0607-0809-0a0b0c0d2b10"
DATA_CHAR_UUID = "02f00000-0000-0000-0000-00000000ff02"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("GoveeHandshake")

HANDSHAKES = [
    bytearray([0x33, 0x11, 0x00, 0x00, 0x00, 0x22]), # Standard
    bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x01]), # Wi-Fi
    bytearray([0xaa, 0x01, 0x00, 0x00, 0x00, 0xab]), # Alternative (Sum)
    bytearray([0xaa, 0x01, 0x00, 0x00, 0x00, 0xab]), # Alternative (XOR) - Same here
]

def notification_handler(sender, data):
    logger.info(f"NOTIFICATION [{sender}]: {data.hex()}")

async def main():
    print(f"--- 🔍 Connecting to {DEVICE_MAC} ---")
    device = await BleakScanner.find_device_by_address(DEVICE_MAC, timeout=20.0)
    if not device:
        print("Device not found.")
        return

    async with BleakClient(device) as client:
        print(f"✅ Connected!")
        
        await client.start_notify(NOTIFY_UUID, notification_handler)
        await client.start_notify(DATA_CHAR_UUID, notification_handler)
        
        for i, handshake in enumerate(HANDSHAKES):
            print(f"\n🔑 Trying Handshake #{i+1}: {handshake.hex()}")
            try:
                await client.write_gatt_char(CONTROL_UUID, handshake)
                print("   Sent. Waiting for data...")
            except Exception as e:
                print(f"   Failed to send handshake: {e}")
            
            # Wait and check ff02
            for _ in range(5):
                await asyncio.sleep(1.0)
                try:
                    val = await client.read_gatt_char(DATA_CHAR_UUID)
                    logger.info(f"READ {DATA_CHAR_UUID}: {val.hex()}")
                except Exception as e:
                    logger.logger.error(f"Read failed: {e}")

        print("\n🚀 Monitoring for 10 more seconds...")
        await asyncio.sleep(10.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
