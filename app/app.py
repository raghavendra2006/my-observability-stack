from flask import Flask, request
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
import logging, json, time, datetime

app = Flask(__name__)

# ---------- JSON LOGGER ----------
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        if hasattr(record, "extra_data"):
            log.update(record.extra_data)
        return json.dumps(log)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# ---------- PROMETHEUS METRICS ----------
REQUEST_COUNT = Counter(
    "flask_app_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "flask_app_request_latency_seconds",
    "Request latency",
    ["endpoint"],
    buckets=(0.1, 0.2, 0.3, 0.5, 1, 2)
)

@app.route("/hello")
def hello():
    start = time.time()
    status = 200
    try:
        app.logger.info(
            "Hello endpoint hit",
            extra={"extra_data": {
                "endpoint": "/hello",
                "method": request.method,
                "user_agent": request.headers.get("User-Agent")
            }}
        )
        return "Hello from Flask!", 200
    finally:
        duration = time.time() - start
        REQUEST_COUNT.labels(request.method, "/hello", status).inc()
        REQUEST_LATENCY.labels("/hello").observe(duration)

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
