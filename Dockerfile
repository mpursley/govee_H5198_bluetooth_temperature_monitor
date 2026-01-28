FROM python:3.9-slim

# Install system dependencies for Bluetooth
# bluez is required for bluetoothctl and tools
RUN apt-get update && apt-get install -y \
    bluez \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY govee_logger.py .

# Create directory for logs
RUN mkdir -p /app/temperature_logs

# Run the logger. Default to 60 seconds if not specified, but this can be overridden.
# The sync loop allows it to wait for connection.
CMD ["python", "-u", "govee_logger.py", "3600"]
