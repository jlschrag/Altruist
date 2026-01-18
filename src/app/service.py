import logging
from datetime import date, datetime, timedelta
from typing import List

from dal import MetricsDAL, RedisDAL
from models import Metric
from prometheus_metrics.connection import push_metrics
from prometheus_metrics.metrics_definitions import cache_hit_counter, cache_miss_counter

"""
This class shows an example Application Layer class.

The metrics service has the dal injected and performs business logic.
"""

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MetricsService:
    def __init__(self, repo: MetricsDAL):
        self.repo = repo

    async def upsert_metric(self, metric: Metric) -> Metric:
        existing_metrics = await self.repo.get_metrics_for([metric.date])
        if len(existing_metrics) == 0:
            return await self.repo.create(metric)
        else:
            existing_metrics[0].mttr = metric.mttr
            existing_metrics[0].open_findings = metric.open_findings
            existing_metrics[0].closed_findings = metric.closed_findings
            return await self.repo.update(existing_metrics[0])

    async def get_metrics_between(self, start_date: date, end_date: date) -> List[Metric]:
        dates = self.dates_between(start_date, end_date)
        return await self.get_metrics_for((dates))

    async def get_metrics_for(self, dates: List[datetime]) -> List[Metric]:
        metrics = await self.repo.get_metrics_for(dates)
        return self.map_empty_metrics(metrics, dates)

    def dates_between(self, start_date: date, end_date: date) -> List[date]:
        return [
            (start_date + timedelta(days=i))
            for i in range((end_date - start_date).days + 1)
        ]

    def map_empty_metrics(self, metrics: List[Metric], dates: List[date]) -> List[Metric]:
        """ If the DAL doesn't have a metric, the service layer fills it in with a default. """
        date_set = set([metric.date for metric in metrics])
        for d in dates:
            if d not in date_set:
                # Append a default metric if we don't have one.
                metrics.append(Metric(date=d, mttr=0, open_findings=0, closed_findings=0))
        metrics.sort(key=lambda metric: metric.date)
        return metrics


class RedisService:
    def __init__(self, dal: RedisDAL):
        self.dal = dal

    def cache_set(self, key: str, value: str, ttl: int = 60) -> bool:
        return self.dal.cache_set(key, value, ttl)

    def cache_get(self, key: str) -> str | None:
        value = self.dal.cache_get(key)
        if value is not None:
            logger.info(f"cache_get: key={key} MISS")
            cache_hit_counter.inc()
            push_metrics()
        else:
            cache_miss_counter.inc()
            logger.info(f"cache_get: key={key} HIT")
            push_metrics()
        return value

    def ping(self) -> bool:
        return self.dal.ping_redis()
