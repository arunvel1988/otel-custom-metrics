import os
import time
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
meter_provider = setup_otel_sdk()
FlaskInstrumentor().instrument_app(app)

# Create a meter and counters
meter = metrics.get_meter(os.getenv("OTEL_SERVICE_NAME", "otel-metrics-demo"))

request_counter = meter.create_counter(
    name="http.server.requests",
    description="Total number of HTTP requests received.",
    unit="{requests}"
)

active_requests = meter.create_up_down_counter(
    name="http.server.active_requests",
    description="Number of in-flight requests.",
    unit="{requests}"
)

@app.route('/')
def hello():
    request_counter.add(1, {"http.route": request.path})
    active_requests.add(1)
    
    # Simulate processing time
    time.sleep(1)

    # Decrement active requests after processing
    active_requests.add(-1)

    # Fancy HTML response
    return (
        "<h1 style='color:#4CAF50;'>🚀 Welcome to OpenTelemetry Metrics Demo! 🚀</h1>"
        "<p style='font-size:18px;'>Your requests are being monitored in real-time with OpenTelemetry.</p>"
        "<p style='font-size:16px;'>✅ Active Requests: tracked via <b>http.server.active_requests</b></p>"
        "<p style='font-size:16px;'>📊 Total Requests: tracked via <b>http.server.requests</b></p>"
        "<p style='font-size:16px;'>🔍 Refresh this page multiple times to see metrics update in your OTLP collector!</p>"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
