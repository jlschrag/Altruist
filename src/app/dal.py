import os
import redis
from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Metric, UserRestrictions


"""
This class shows an example persistence layer for our application.

This particular DAL is for the metrics table and we make sure that in this use case we always have
user restrictions injected and verified.

Sometimes we call this a repository after that pattern.
"""


class MetricsDAL():
    db: AsyncSession

    def __init__(self, db: AsyncSession, user_restrictions: UserRestrictions):
        self.db = db
        self.user_restrictions = user_restrictions

    async def create(self, metric: Metric):
        self.user_restrictions.assert_edit_metrics()

        metric.org_id = self.user_restrictions.org_id
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def update(self, metric: Metric):
        self.user_restrictions.assert_edit_metrics()

        metric.org_id = self.user_restrictions.org_id
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def get_metrics_for(self, list_of_dates: List[datetime]) -> List[Metric]:
        self.user_restrictions.assert_view_metrics()

        query = (
            select(Metric)
            .where(Metric.org_id == self.user_restrictions.org_id)
            .where(Metric.date.in_(list_of_dates))
            .order_by(Metric.date)
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class RedisDAL:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True,
        )

    def ping_redis(self) -> bool:
        return self.redis_client.ping()

    def cache_set(self, key: str, value: str, ttl: int = 60) -> bool:
        return self.redis_client.setex(key, ttl, value)

    def cache_get(self, key: str) -> str | None:
        return self.redis_client.get(key)
