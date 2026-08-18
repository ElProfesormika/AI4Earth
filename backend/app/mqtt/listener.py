import asyncio
import json
import logging
import random
from datetime import datetime

import paho.mqtt.client as mqtt

from app.config import settings
from app.db.models import Bin, Classification
from app.db.session import SessionLocal
from app.services.wqs_service import WASTE_CLASSES, compute_and_store_wqs

log = logging.getLogger(__name__)

WASTE_CLASSES_WEIGHTED = WASTE_CLASSES + WASTE_CLASSES  # duplicate for distribution


def _on_connect(client, userdata, flags, rc, props=None):
    log.info("MQTT connected rc=%s", rc)
    prefix = settings.mqtt_topic_prefix
    client.subscribe(f"{prefix}/bins/+/telemetry", qos=1)
    client.subscribe(f"{prefix}/bins/register", qos=1)


def _register_bins(db, payload: list[dict]):
    for item in payload:
        existing = db.get(Bin, item["id"])
        if existing:
            continue
        db.add(
            Bin(
                id=item["id"],
                name=item["name"],
                district=item["district"],
                lat=item["lat"],
                lon=item["lon"],
                capacity_l=120,
                qr_code=f"QR-{item['id']:04d}",
            )
        )
    db.commit()


def _maybe_add_classification(db, bin_id: int, fill_pct: float):
    if random.random() > 0.15:
        return
    dominant = WASTE_CLASSES[bin_id % len(WASTE_CLASSES)]
    waste_class = dominant if random.random() > 0.2 else random.choice(WASTE_CLASSES)
    db.add(
        Classification(
            bin_id=bin_id,
            ts=datetime.utcnow(),
            waste_class=waste_class,
            confidence=round(random.uniform(0.75, 0.99), 2),
            item_count=random.randint(1, 5),
        )
    )
    compute_and_store_wqs(db, bin_id)


def _on_message(client, userdata, msg):
    try:
        topic = msg.topic
        prefix = settings.mqtt_topic_prefix

        if topic == f"{prefix}/bins/register":
            payload = json.loads(msg.payload.decode())
            with SessionLocal() as db:
                _register_bins(db, payload)
            return

        if "/telemetry" in topic:
            payload = json.loads(msg.payload.decode())
            bin_id = int(topic.split("/")[-2])
            with SessionLocal() as db:
                from app.db.models import Telemetry

                db.add(
                    Telemetry(
                        ts=datetime.utcnow(),
                        bin_id=bin_id,
                        fill_pct=payload["fill_pct"],
                        weight_kg=payload["weight_kg"],
                        temp_c=payload["temp_c"],
                        humidity_pct=payload["humidity_pct"],
                        gas_ppm=payload["gas_ppm"],
                        source=payload.get("source", "simulator"),
                    )
                )
                _maybe_add_classification(db, bin_id, payload["fill_pct"])
                db.commit()
    except Exception as e:
        log.exception("MQTT ingest failed: %s", e)


def start_mqtt_listener():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="backend-listener")
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, client.loop_forever)
