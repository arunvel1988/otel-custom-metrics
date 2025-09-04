import os
import time
from flask import Flask, request

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.semconv.resource import ResourceAttributes

def setup_otel_sdk():
    # Configure the resource with service info
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "otel-metrics-demo"),
        ResourceAttributes.SERVICE_VERSION: "0.1.0",
    })

    # Create an OTLP exporter
    exporter = OTLPMetricExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/metrics"
    )

    # Create a metric reader that will periodically export metrics
    reader = PeriodicExportingMetricReader(
        exporter=exporter,
        export_interval_millis=3000  # Export every 3 seconds
    )

    # Initialize the MeterProvider with resource and reader
    provider = MeterProvider(resource=resource, metric_readers=[reader])

    # Set the global MeterProvider
    metrics.set_meter_provider(provider)

    return provider

app = Flask(__name__)

# Initialize OpenTelemetry SDK
meter_provider = setup_otel_sdk()

@app.route('/')
def hello():
    return (
        "<h1>🚀 Welcome to OpenTelemetry Metrics Demo! 🚀</h1>"
        "<p>This Flask app is actively generating metrics to your OTLP collector.</p>"
        "<p>Check your collector dashboard to see metrics in real-time!</p>"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
