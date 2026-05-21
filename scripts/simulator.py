
import json
import time
import random
import logging
from datetime import datetime, timezone
from azure.eventhub import EventHubProducerClient, EventData

# ─────────────────────────────────────────────
#  CONFIGURATION — Update these values
# ─────────────────────────────────────────────
CONNECTION_STR = "PASTE_YOUR_CONNECTION_STRING_HERE"
EVENT_HUB_NAME = "voltgrid-events"

NUM_DEVICES = 10          # Total number of simulated devices
SEND_INTERVAL = 2         # Seconds between each message
ANOMALY_CHANCE = 0.05     # 5% chance of injecting an anomaly reading
# ─────────────────────────────────────────────

# Set up logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("VoltGridSimulator")

# ─────────────────────────────────────────────
#  DEVICE REGISTRY
#  Each device has a type that shapes its telemetry
# ─────────────────────────────────────────────
DEVICE_TYPES = ["smart_meter", "solar_panel", "battery"]

devices = [
    {
        "id": f"device-{str(i).zfill(3)}",
        "type": DEVICE_TYPES[i % len(DEVICE_TYPES)],
        "location": random.choice(["Lagos-North", "Lagos-South", "Abuja", "PH", "Kano"]),
        "battery_charge": random.uniform(20, 100),  # Only used for battery devices
    }
    for i in range(1, NUM_DEVICES + 1)
]


def generate_smart_meter_data(device: dict, anomaly: bool) -> dict:
    """Simulates a household/commercial smart meter."""
    power_usage = round(random.uniform(80, 180), 2) if anomaly else round(random.uniform(20, 150), 2)
    voltage = round(random.uniform(180, 200), 2) if anomaly else round(random.uniform(210, 240), 2)
    current = round(power_usage / voltage, 3)
    return {
        "deviceId": device["id"],
        "deviceType": device["type"],
        "location": device["location"],
        "powerUsage_kW": power_usage,
        "voltage_V": voltage,
        "current_A": current,
        "anomaly": anomaly,
        "status": "WARNING" if anomaly else "OK",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def generate_solar_panel_data(device: dict, anomaly: bool) -> dict:
    """
    Simulates a solar panel. Power generation varies with simulated time of day.
    Negative powerUsage means the panel is exporting energy back to the grid.
    """
    hour = datetime.now().hour
    # Simulate solar irradiance peak around midday
    solar_factor = max(0, 1 - abs(hour - 13) / 8)
    generation = round(random.uniform(0, 50) * solar_factor, 2)
    power_usage = -generation  # Negative = generating / exporting
    if anomaly:
        power_usage = round(random.uniform(-5, 5), 2)  # Near-zero output is suspicious

    return {
        "deviceId": device["id"],
        "deviceType": device["type"],
        "location": device["location"],
        "powerUsage_kW": power_usage,
        "generation_kW": generation,
        "voltage_V": round(random.uniform(380, 420), 2),
        "solarFactor": round(solar_factor, 3),
        "anomaly": anomaly,
        "status": "LOW_OUTPUT" if anomaly else "OK",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def generate_battery_data(device: dict, anomaly: bool) -> dict:
    """
    Simulates a battery storage unit. Tracks charge level over time.
    Anomaly = overcharge or critical low.
    """
    # Simulate gradual charge/discharge
    delta = random.uniform(-3, 3)
    device["battery_charge"] = max(0, min(100, device["battery_charge"] + delta))
    charge = round(device["battery_charge"], 2)

    if anomaly:
        charge = random.choice([round(random.uniform(0, 5), 2), round(random.uniform(96, 100), 2)])

    status = "OK"
    if charge < 10:
        status = "CRITICAL_LOW"
    elif charge > 95:
        status = "OVERCHARGE"

    return {
        "deviceId": device["id"],
        "deviceType": device["type"],
        "location": device["location"],
        "chargeLevel_pct": charge,
        "powerUsage_kW": round(random.uniform(-20, 20), 2),  # Negative = charging
        "voltage_V": round(random.uniform(48, 52), 2),
        "temperature_C": round(random.uniform(25, 45), 1),
        "anomaly": anomaly,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


GENERATORS = {
    "smart_meter": generate_smart_meter_data,
    "solar_panel": generate_solar_panel_data,
    "battery": generate_battery_data,
}


def generate_telemetry(device: dict) -> dict:
    """Pick the right generator for this device type and create a reading."""
    anomaly = random.random() < ANOMALY_CHANCE
    generator = GENERATORS[device["type"]]
    return generator(device, anomaly)


def send_telemetry(producer: EventHubProducerClient, data: dict) -> None:
    """Send a single telemetry event to Azure Event Hub."""
    event_batch = producer.create_batch()
    event_batch.add(EventData(json.dumps(data)))
    producer.send_batch(event_batch)


def format_log_line(data: dict) -> str:
    """Build a readable one-line summary for the console."""
    icon = "⚠️ " if data.get("anomaly") else "✓ "
    device_type = data["deviceType"]
    device_id = data["deviceId"]
    location = data["location"]
    status = data.get("status", "OK")

    if device_type == "smart_meter":
        detail = f"{data['powerUsage_kW']}kW @ {data['voltage_V']}V"
    elif device_type == "solar_panel":
        detail = f"gen={data['generation_kW']}kW  export={abs(data['powerUsage_kW'])}kW"
    else:  # battery
        detail = f"charge={data['chargeLevel_pct']}%  temp={data['temperature_C']}°C"

    return f"{icon}[{device_type}] {device_id} ({location}) — {detail} [{status}]"


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    if CONNECTION_STR == "PASTE_YOUR_CONNECTION_STRING_HERE":
        log.error("❌ CONNECTION_STR is not set. Open this file and paste your Azure Event Hub connection string.")
        return

    log.info("🚀 VoltGrid  Simulator starting...")
    log.info(f"   Devices : {NUM_DEVICES}  |  Types: {DEVICE_TYPES}")
    log.info(f"   Interval: {SEND_INTERVAL}s  |  Anomaly rate: {int(ANOMALY_CHANCE * 100)}%")
    log.info("   Press Ctrl+C to stop.\n")

    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENT_HUB_NAME
    )

    messages_sent = 0

    try:
        while True:
            device = random.choice(devices)
            data = generate_telemetry(device)

            send_telemetry(producer, data)
            messages_sent += 1

            log.info(f"[#{messages_sent:05d}] {format_log_line(data)}")
            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        log.info(f"\n⏹  Simulator stopped. Total messages sent: {messages_sent}")

    except Exception as e:
        log.error(f"❌ Unexpected error: {e}")

    finally:
        producer.close()
        log.info("Producer connection closed.")


if __name__ == "__main__":
    main()
