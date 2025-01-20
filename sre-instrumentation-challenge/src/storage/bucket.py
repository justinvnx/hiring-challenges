from typing import Dict
from flask import Blueprint, jsonify, request, Response
from prometheus_client import Histogram
from flask.typing import ResponseReturnValue
import time
from functools import wraps

# Define the Prometheus Histogram
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds', 'Histogram of HTTP request durations',
    ['method', 'path', 'status_code']
)

# Create a Blueprint
bucket_blueprint = Blueprint("zones", __name__)

# In-memory data store
data: Dict[str, bytes] = {}

# Decorator for recording metrics
def record_metrics(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            response = func(*args, **kwargs)
            # If response is a tuple, extract status code
            if isinstance(response, tuple) and len(response) > 1:
                status_code = response[1]
            else:
                status_code = 200
        except Exception as e:
            status_code = 500
            response = jsonify({"error": "Internal server error"}), 500
        finally:
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=request.method,
                path=request.path,
                status_code=status_code
            ).observe(duration)
        return response
    return wrapper

# Routes
@bucket_blueprint.route("/buckets/<id>")
@record_metrics
def get_bucket(id: str) -> ResponseReturnValue:
    if id in data.keys():
        return data.get(id), 200, {"Content-Type": "application/json"}
    return jsonify({"error": "wtf bro"}), 404, {"Content-Type": "application/json"}


@bucket_blueprint.route("/buckets/<id>", methods=["PUT"])
@record_metrics
def put_bucket(id: str) -> ResponseReturnValue:
    data[id] = request.get_data()
    return "", 200


@bucket_blueprint.route("/buckets/<id>", methods=["DELETE"])
@record_metrics
def delete_bucket(id: str) -> ResponseReturnValue:
    if id in data.keys():
        data.pop(id, None)
        return "", 500
    return jsonify({"error": "bad request"}), 400, {"Content-Type": "application/json"}

@bucket_blueprint.route("/test_metrics")
def test_metrics():
    http_request_duration_seconds.labels(
        method="GET",
        path="/test_metrics",
        status_code="200"
    ).observe(0.123)  # Simulate a fixed duration
    return "Metrics recorded!", 200

