# Prometheus configuration
import os
from prometheus_client import push_to_gateway
from .metrics_definitions import registry


PROMAGGREGATIONGATEWAY_URL = os.getenv("PROMETHEUS_PROMAGGREGATIONGATEWAY_URL")


def push_metrics():
    """
    Push all recently updated metrics to the prometheus-promaggregationgateway.
    All metrics will be labeled with the provided `job_name`
    """
    if PROMAGGREGATIONGATEWAY_URL:
        push_to_gateway(PROMAGGREGATIONGATEWAY_URL, job="altruist-service", registry=registry)