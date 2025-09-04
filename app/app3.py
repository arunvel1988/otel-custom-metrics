import os
from flask import Flask, request
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.flask import FlaskInstrumentor

def setup_otel_sdk():
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "otel-metrics-demo"),
        ResourceAttributes.SERVICE_VERSION: "0.1.0",
    })

    exporter = OTLPMetricExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/metrics"
    )

    reader = PeriodicExportingMetricReader(
        exporter=exporter,
        export_interval_millis=3000  # Export every 3 seconds
    )

    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)
    return provider

app = Flask(__name__)

# Initialize OpenTelemetry SDK
meter_provider = setup_otel_sdk()

# Instrument Flask with OpenTelemetry
FlaskInstrumentor().instrument_app(app)

# Create a meter and request counter
meter = metrics.get_meter(os.getenv("OTEL_SERVICE_NAME", "otel-metrics-demo"))
request_counter = meter.create_counter(
    name="http.server.requests",
    description="Total number of HTTP requests received.",
    unit="{requests}"
)

@app.route('/')
def hello():
    # Increment the request counter
    request_counter.add(1, {"http.route": request.path})
    
    # Fancy HTML response with emojis
    return (
        "<h1 style='color: #2196F3;'>🎉 Welcome to the OpenTelemetry Metrics Demo! 🎉</h1>"
        "<p style='font-size: 18px;'>This Flask application is actively generating metrics to your OTLP collector.</p>"
        "<p style='font-size: 16px;'>📊 Each visit increments the <b>http.server.requests</b> counter.</p>"
        "<p style='font-size: 16px;'>🌟 Explore your metrics dashboard to see real-time updates and learn OpenTelemetry in action!</p>"
        "<p style='font-size: 16px;'>💡 Tip: Try refreshing this page multiple times to see the request counter increase in your OTLP collector.</p>"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
