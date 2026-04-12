# app/kafka/producer.py
import json
import logging
import ssl
from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

from app.core.config import settings

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None


async def start_producer() -> None:
    """Start the Kafka producer. Called from app lifespan on startup."""
    global _producer

    if not settings.KAFKA_ENABLED:
        logger.info("Kafka disabled (KAFKA_ENABLED=false) — skipping producer startup")
        return

    try:
        ssl_context = ssl.create_default_context()
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            security_protocol="SASL_SSL",
            sasl_mechanism="PLAIN",
            sasl_plain_username=settings.KAFKA_API_KEY,
            sasl_plain_password=settings.KAFKA_API_SECRET,
            ssl_context=ssl_context,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            acks="all",
            enable_idempotence=True,
        )
        await _producer.start()
        logger.info("Kafka producer connected to %s", settings.KAFKA_BOOTSTRAP_SERVERS)
    except Exception as e:
        logger.error("Kafka producer failed to start: %s — continuing without Kafka", e)
        _producer = None


async def stop_producer() -> None:
    """Stop the Kafka producer. Called from app lifespan on shutdown."""
    global _producer

    if _producer is not None:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")


async def publish_event(topic: str, payload: dict[str, Any]) -> None:
    """
    Publish an event to a Kafka topic.

    Fails silently: if Kafka is disabled or unavailable the app continues
    normally — same graceful degradation pattern used for Redis cache.

    Args:
        topic:   Kafka topic name  (e.g. "order.created")
        payload: JSON-serializable dict that becomes the message value
    """
    if _producer is None:
        logger.debug("Kafka unavailable — event '%s' not published", topic)
        return

    try:
        await _producer.send_and_wait(topic, value=payload)
        logger.info("Kafka event published | topic=%s | keys=%s", topic, list(payload.keys()))
    except KafkaConnectionError as e:
        logger.error("Kafka connection error publishing '%s': %s", topic, e)
    except Exception as e:
        logger.error("Unexpected error publishing Kafka event '%s': %s", topic, e)
