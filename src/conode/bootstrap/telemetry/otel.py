import os
from uuid import uuid4

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import (
    SERVICE_INSTANCE_ID,
    SERVICE_NAME,
    Resource,
)
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

    tracer_provider = TracerProvider(
        resource=resource,
    )

    trace_exporter = OTLPSpanExporter(
        endpoint=config.endpoint,
        insecure=True,
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

    trace.set_tracer_provider(
        tracer_provider,
    )

    metric_exporter = OTLPMetricExporter(
        endpoint=config.endpoint,
        insecure=True,
    )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                metric_exporter,
                export_interval_millis=5000,
            ),
        ],
    )

    metrics.set_meter_provider(
        meter_provider,
    )
