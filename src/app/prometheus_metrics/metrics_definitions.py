from prometheus_client import CollectorRegistry, Counter

registry = CollectorRegistry()

cache_hit_counter = Counter(
    "redis_cache_hit_total",
    "Total number of Redis cache hits",
    registry=registry,
)

cache_miss_counter = Counter(
    "redis_cache_miss_total",
    "Total number of Redis cache misses",
    registry=registry,
)

health_api_call_success_gauge = Counter(
    "appomni_app_health_api_call_sucess",
    "metrics to represent the number of sucess calls the health api emitted",
    registry=registry,
)
