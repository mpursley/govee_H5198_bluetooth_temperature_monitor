# Govee H5198 Bluetooth Temperature Monitor & Logger

A Python-based toolset for monitoring and logging data from the **[Govee H5198 WiFi Meat Thermometer](https://us.govee.com/blogs/product-review-blog/use-the-govee-wi-fi-grilling-meat-thermometer-to-cook-meats-your-way)** using Bluetooth Low Energy (BLE).
<img width="800" height="375" alt="image" src="https://github.com/user-attachments/assets/1ddf4ad8-048e-415d-aaa2-3c46cc811b5f" />


This project reverse-engineers the BLE advertisement packets to provide real-time temperature readings and CSV/TXT logging without requiring the official Govee app or cloud service.

> [!NOTE]
> This entire repository was **"vibe coded"** by **[Google Gemini 3](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro)** with no/limited human intervention. Read and review the code before using and contributing updates.

## Features

*   **Auto-Discovery:** Automatically finds your H5198 device (looks for Manufacturer ID `0x2331`), so you don't need to hardcode a MAC address.
*   **Real-Time Monitoring:** Console-based live view of all 4 probes.
*   **Data Logging:** Logs temperature data to timestamped CSV and TXT files.
*   **Robust Syncing:** Waits for all connected probes to report data before starting logs to ensure complete datasets.

## Windows Binaries

For users who don't want to install Python, standalone Windows executables are available in the [Releases](https://github.com/openworldtechio/govee_H5198_bluetooth_temperature_monitor/releases) section.

*   `govee_live_view.exe`: Double-click to start monitoring.
*   `govee_logger.exe`: Run from the command line to specify duration, or double-click to run indefinitely.

## Prerequisites

*   Python 3.7+
*   A Bluetooth Adapter (BLE capable)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/openworldtechio/govee_H5198_bluetooth_temperature_monitor.git
    cd govee_H5198_bluetooth_temperature_monitor
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Live Monitor (`govee_live_view.py`)
View current temperatures in your terminal. This script scans for the device, syncs all probes, and then displays a live-updating status line.

```bash
python govee_live_view.py
```

### 2. Data Logger (`govee_logger.py`)
Logs temperature data to the `temperature_logs/` directory.

**Run indefinitely (until Ctrl+C):**
```bash
python govee_logger.py
```

**Run for a specific duration (in minutes):**
```bash
python govee_logger.py 60       # Run for 1 hour
python govee_logger.py 10       # Run for 10 minutes
python govee_logger.py 0.5      # Run for 30 seconds
```

## Output

Log files are saved in the `temperature_logs/` folder with unique timestamps:

*   `temperature_log_YYYY-MM-DD_HH-MM-SS.csv` (Easy to import into Excel)
```
Time,P1,P2,P3,P4
12:49:45,114.8°F,77.0°F,77.0°F,102.2°F
12:49:50,114.8°F,77.0°F,77.0°F,102.2°F
12:49:55,114.8°F,77.0°F,77.0°F,102.2°F
12:50:00,114.8°F,77.0°F,77.0°F,102.2°F
```

*   `temperature_log_YYYY-MM-DD_HH-MM-SS.txt` (Human-readable format)
E.g.
```
Time       |       P1 |       P2 |       P3 |       P4
-------------------------------------------------------
12:49:35   |  114.8°F |   77.0°F |       -- |       --
12:49:40   |  114.8°F |   77.0°F |   77.0°F |  100.4°F
12:49:45   |  114.8°F |   77.0°F |   77.0°F |  102.2°F
12:49:50   |  114.8°F |   77.0°F |   77.0°F |  102.2°F
12:49:55   |  114.8°F |   77.0°F |   77.0°F |  102.2°F
```

## Troubleshooting

*   **Sync Timeout:** If some probes are unplugged, the "Syncing" phase will time out after 60 seconds and proceed with whichever probes were found.
*   **Bluetooth Permissions:** On Linux/Raspberry Pi, you may need to run with `sudo` or configure bluetooth permissions.
