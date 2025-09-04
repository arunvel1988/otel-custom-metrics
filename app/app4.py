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
   # Configuration code remains the same
   # ...

app = Flask(__name__)

# Initialize OpenTelemetry SDK
meter_provider = setup_otel_sdk()

# Instrument Flask with OpenTelemetry
FlaskInstrumentor().instrument_app(app)

# Create a meter
meter = metrics.get_meter(os.getenv("OTEL_SERVICE_NAME", "otel-metrics-demo"))

# Create a request counter
request_counter = meter.create_counter(
   name="http.server.requests",
   description="Total number of HTTP requests received.",
   unit="{requests}"
)

# Create an active requests up-down counter
active_requests = meter.create_up_down_counter(
   name="http.server.active_requests",
   description="Number of in-flight requests.",
   unit="{requests}"
)

@app.route('/')
def hello():
   # Increment the request counter with route attribute
   request_counter.add(1, {"http.route": request.path})

   # Increment active requests counter
   active_requests.add(1)

   # Simulate processing time
   time.sleep(1)

   result = "Hello world!"

   # Decrement active requests counter
   active_requests.add(-1)

   return result

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8000, debug=True)
