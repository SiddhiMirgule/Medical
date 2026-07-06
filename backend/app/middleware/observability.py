"""OpenTelemetry and Prometheus observability setup."""

from __future__ import annotations

from prometheus_client import Counter, Histogram, generate_latest

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "medverify_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "medverify_request_duration_seconds",
    "Request latency",
    ["endpoint"],
)
RETRIEVAL_LATENCY = Histogram(
    "medverify_retrieval_duration_seconds",
    "Retrieval pipeline latency",
)
LLM_LATENCY = Histogram(
    "medverify_llm_duration_seconds",
    "LLM invocation latency",
    ["model"],
)
HALLUCINATION_RATE = Counter(
    "medverify_hallucinations_total",
    "Detected hallucinations",
    ["classification"],
)


def setup_telemetry() -> None:
    """Initialize OpenTelemetry tracing if configured."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

        provider = TracerProvider()
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        logger.info("opentelemetry_initialized")
    except Exception as exc:
        logger.warning("opentelemetry_setup_failed", error=str(exc))


def get_metrics() -> bytes:
    return generate_latest()
