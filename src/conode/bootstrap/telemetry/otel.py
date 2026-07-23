import os
from uuid import uuid4

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import SERVICE_INSTANCE_ID, SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from conode.infrastructure.config import OTELConfig


def configure_telemetry(config: OTELConfig) -> None:
    if not config.enabled:
        return

    resource = Resource.create(
        {
            SERVICE_NAME: "conode",
            SERVICE_INSTANCE_ID: f"conode-{os.getpid()}-{uuid4().hex[:8]}",
        },
    )

    provider = TracerProvider(
        resource=resource,
    )

    exporter = OTLPSpanExporter(
        endpoint=config.endpoint,
        insecure=True,
    )

    processor = BatchSpanProcessor(
        exporter,
    )

    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
