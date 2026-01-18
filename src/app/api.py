from http.client import HTTPException
from typing import List
from fastapi import APIRouter, Depends, Query

from config import get_metrics_service, get_redis_service
from prometheus_metrics.connection import push_metrics
from prometheus_metrics.metrics_definitions import health_api_call_success_gauge
from schemas import (
    DatePeriodParam,
    MetricChartResponse,
    MetricComparisonResponse,
    UpsertMetricRequest,
)
from service import MetricsService, RedisService

"""
The api controller functions. 

Responsibilities:
    Declaratively define routes to be handled.
    Declaratively define service layer dependencies to be injected.
    Take request inputs and map them to the service layer.
    If multiple services need to be chained together to get a response, do that here.
        Don't over do it though. If you always need the same two services to get 
        the job done that's probably the same service in two places.
    Map the service layer output to outbound responses using schema DTOs and ViewModels.
"""

router = APIRouter(prefix="/altruist/api/v1")

@router.get("/")
async def root(fail: str = None):
    if fail:
        raise HTTPException(status_code=400, detail="forced Error")
    return {"message": "I'm alive!"}

@router.get("/health")
async def read_health():
    health_api_call_success_gauge.inc(1)
    push_metrics()
    return {"Healthy"}


@router.post("/metric")
async def create_metric(
    metric: UpsertMetricRequest,
    service: MetricsService = Depends(get_metrics_service)
):
    return await service.upsert_metric(UpsertMetricRequest.to_model(metric))


@router.get("/compare-mttr", response_model=MetricComparisonResponse)
async def compare_mttr_metrics(
    period: DatePeriodParam = Depends(),
    service: MetricsService = Depends(get_metrics_service)
) -> List[MetricComparisonResponse]:
    (current, past) = await service.get_metrics_for([period.start, period.end])
    return MetricComparisonResponse.from_model(current, past, lambda metric: metric.mttr)


@router.get("/compare-open", response_model=MetricComparisonResponse)
async def compare_open_metrics(
    period: DatePeriodParam = Depends(),
    service: MetricsService = Depends(get_metrics_service)
) -> List[MetricComparisonResponse]:
    (current, past) = await service.get_metrics_for([period.start, period.end])
    return MetricComparisonResponse.from_model(current, past, lambda metric: metric.open_findings)


@router.get("/compare-closed", response_model=MetricComparisonResponse)
async def compare_closed_metrics(
    period: DatePeriodParam = Depends(),
    service: MetricsService = Depends(get_metrics_service)
) -> List[MetricComparisonResponse]:
    (current, past) = await service.get_metrics_for([period.start, period.end])
    return MetricComparisonResponse.from_model(current, past, lambda metric: metric.closed_findings)


@router.get("/chart-mttr", response_model=MetricChartResponse)
async def chart_mttr_metrics(
    period: DatePeriodParam = Depends(),
    service: MetricsService = Depends(get_metrics_service)
) -> List[MetricChartResponse]:
    metrics = await service.get_metrics_between(period.start, period.end)
    return MetricChartResponse.from_model(metrics, lambda metric: metric.mttr)


@router.get("/chart-open", response_model=MetricChartResponse)
async def chart_open_metrics(
    period: DatePeriodParam = Depends(),
    service: MetricsService = Depends(get_metrics_service)
) -> List[MetricComparisonResponse]:
    metrics = await service.get_metrics_between(period.start, period.end)
    return MetricChartResponse.from_model(metrics, lambda metric: metric.open_findings)

@router.get("/redis_ping")
def redis_ping(redis_service: RedisService = Depends(get_redis_service)):
    try:
        if redis_service.ping():
            return {"status": "Redis is alive"}
    except Exception as e:
        return {"status": "Redis error", "detail": str(e)}

@router.get("/cache_set")
def set_cache(
    key: str = Query(...),
    value: str = Query(...),
    ttl: int = Query(60),
    redis_service: RedisService = Depends(get_redis_service)
):
    success = redis_service.cache_set(key, value, ttl)
    return {"status": "ok" if success else "failed"}

@router.get("/cache_get")
def get_cache(
    key: str = Query(...),
    redis_service: RedisService = Depends(get_redis_service)
):
    value = redis_service.cache_get(key)
    if value is None:
        return {"status": "not found"}
    return {"status": "ok", "value": value}
