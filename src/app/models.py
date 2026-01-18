from typing import List
from pydantic import BaseModel

from sqlalchemy import Column, Date, Float, Integer
from sqlalchemy.orm import DeclarativeBase


"""
These models define our domain models and the innermost layer of our application.

You'll notice that I'm making a pragmatic decision to use SQLAlchemy to define the models that will
always live in the database. The pragmatism has limits though.
DO:   `from sqlalchemy import stuff`
DO:   `from pydantic import stuff`
DO:   `from polars import stuff`
Reasoning: By bending the rules for persistence libs a bit we can avoid a lot of boilerplate.

DONT: `from metrics.dal import stuff`
DONT: `from metrics.services import stuff`
DONT: `from metrics.api import stuff`
DONT: `from fastapi import stuff`
DONT: `from dagster import stuff`
Reasoning: These are presentation layer libs or imports from higher layers. By not including them 
    we save ourselves the headaches involved with HTTP problems while we're in an ETL pipeline.
"""


# Sqlalchemy base models 
class Base(DeclarativeBase):
    pass


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer)
    date = Column(Date)
    mttr = Column(Float)
    open_findings = Column(Integer)
    closed_findings = Column(Integer)


# Non DB Model
class AuthException(Exception):
    message: str
    def __init__(self, message: str):
        self.message = message


class UserRestrictions(BaseModel):
    org_id: str
    roles: List[str]

    def is_admin(self) -> bool:
        return "admin" in self.roles

    def assert_view_metrics(self) -> bool:
        if not self.is_admin() and "view-metrics" not in self.roles:
            raise AuthException("User view edit metrics")

    def assert_edit_metrics(self) -> None:
        if not self.is_admin() and "edit-metrics" not in self.roles:
            raise AuthException("User cannot edit metrics")
