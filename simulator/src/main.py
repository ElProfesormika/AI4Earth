"""Simulate 40 bins publishing telemetry over MQTT."""
import json
import math
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

import paho.mqtt.client as mqtt
import yaml

CONFIG = yaml.safe_load(open(Path(__file__).parent.parent / "config" / "city_config.yaml"))
MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "smartwaste")
TICK_MS = int(os.getenv("SIMULATOR_TICK_MS", 5000))
COMPRESSED_MIN_PER_TICK = 5


class Bin:
    def __init__(
        self,
        bin_id: int,
        name: str,
        district: str,
        lat: float,
        lon: float,
        fill_rate_range: tuple,
    ):
        self.id, self.name, self.district = bin_id, name, district
        self.lat, self.lon = lat, lon
        self.fill_pct = random.uniform(5, 30)
        self.weight_kg = 0.0
        self.fill_rate_range = fill_rate_range
        self.temp_offset = random.uniform(-1.5, 1.5)
        self.gas_baseline = random.uniform(50, 150)

    def step(self, sim_now: datetime, weather: dict, event_multiplier: float):
        hourly = random.uniform(*self.fill_rate_range) * event_multiplier
        dpct = hourly * (COMPRESSED_MIN_PER_TICK / 60.0)
        self.fill_pct = min(100.0, self.fill_pct + dpct)
        if self.fill_pct >= 95 and random.random() < CONFIG["collection"]["reset_prob_on_full"]:
            self.fill_pct = 5.0
        self.weight_kg = round(self.fill_pct * 0.6 + random.gauss(0, 0.5), 2)
        gas = self.gas_baseline + self.fill_pct * 3 + weather["temp_c"] * 2
        gas *= 1.5 if weather["humidity_pct"] > 80 else 1.0
        return {
            "bin_id": self.id,
            "ts": sim_now.isoformat(),
            "fill_pct": round(self.fill_pct, 1),
            "weight_kg": self.weight_kg,
            "temp_c": round(weather["temp_c"] + self.temp_offset, 1),
            "humidity_pct": round(weather["humidity_pct"], 1),
            "gas_ppm": round(gas, 1),
            "source": "simulator",
        }


def build_bins() -> list[Bin]:
    bins = []
    bin_id = 1
    for d in CONFIG["districts"]:
        lat_c, lon_c = d["center"]
        for i in range(d["bins"]):
            lat = lat_c + random.uniform(-0.008, 0.008)
            lon = lon_c + random.uniform(-0.008, 0.008)
            bins.append(
                Bin(
                    bin_id,
                    f"{d['name']}-{i + 1}",
                    d["name"],
                    lat,
                    lon,
                    tuple(d["fill_rate_per_hour"]),
                )
            )
            bin_id += 1
    return bins


def weather_at(sim_now: datetime) -> dict:
    h = sim_now.hour + sim_now.minute / 60
    base = CONFIG["weather"]["base_temp_c"]
    amp = CONFIG["weather"]["daily_amplitude_c"]
    temp = base + amp * math.sin((h - 6) / 24 * 2 * math.pi)
    hum = CONFIG["weather"]["base_humidity_pct"] - (temp - base) * 1.5
    return {"temp_c": temp, "humidity_pct": max(30, min(95, hum))}


def active_multiplier(bin_: Bin, sim_now: datetime, start_time: datetime) -> float:
    for e in CONFIG["events"]:
        if bin_.district != e["district"]:
            continue
        e_start = start_time + timedelta(hours=e["start_offset_hours"])
        e_end = e_start + timedelta(hours=e["duration_hours"])
        if e_start <= sim_now <= e_end:
            return e["multiplier"]
    return 1.0


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="simulator")
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()

    bins = build_bins()
    client.publish(
        f"{TOPIC_PREFIX}/bins/register",
        json.dumps(
            [
                {
                    "id": b.id,
                    "name": b.name,
                    "district": b.district,
                    "lat": b.lat,
                    "lon": b.lon,
                }
                for b in bins
            ]
        ),
        qos=1,
    )

    sim_now = datetime.utcnow()
    start = sim_now
    print(f"Simulator running: {len(bins)} bins, {COMPRESSED_MIN_PER_TICK} min per tick")
    while True:
        w = weather_at(sim_now)
        for b in bins:
            payload = b.step(sim_now, w, active_multiplier(b, sim_now, start))
            client.publish(
                f"{TOPIC_PREFIX}/bins/{b.id}/telemetry",
                json.dumps(payload),
                qos=1,
            )
        sim_now += timedelta(minutes=COMPRESSED_MIN_PER_TICK)
        time.sleep(TICK_MS / 1000.0)


if __name__ == "__main__":
    main()
