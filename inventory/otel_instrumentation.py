from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def init_tracing_and_metrics(app, service_name: str):
    #les traces
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({"service.name": service_name})
        )
    )
    span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    trace.get_tracer_provider().add_span_processor(span_processor)
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()

    #les matrices
    reader = PrometheusMetricReader()
    metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))
    meter = metrics.get_meter(service_name)

    # Exemple de compteur pour les requêtes HTTP
    request_counter = meter.create_counter(
        "http_requests_total",
        description="Total des requêtes HTTP reçues"
    )

    @app.middleware("http")
    async def count_requests(request, call_next):
        request_counter.add(1, {"path": request.url.path, "method": request.method})
        response = await call_next(request)
        return response

    return reader  # on peut exposer pour Prometheus
