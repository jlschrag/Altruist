from datetime import date
from typing import Callable, List, Union
from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from models import AuthException, Metric, UserRestrictions


"""
These schemas define our request and response DTOs or ViewModels.

Schemas define the outward facing application shape and often come with methods 
like from_model or to_model that help map data between the domain models and what 
we see on the outside.

There are two main types.
    Types that take api input to create service layer parameters.
    Types that take serviece layer output and map it to api output.

These live in the application layer.
"""


MetricSelector = Callable[[Metric], Union[float, int]]


class AuthToken:
    org_id: str
    roles: List[str]

    def __init__(self, header: str):
        """
        Defines a fake auth token for parsing.
        Do your own token verification and decoding here.

        This could use HTTPException to return a 401 if the token is invalid, however I opted to
        return a domain exception and let the auth_exception_handler in the __init__.py handle it.

        Is that a good pattern for this use case? Maybe not, but I left it in as an example.
        """
        header = "Auth: 123 admin" if header == "Auth" else header
        if header is None or not header.startswith("Auth"):
            raise AuthException("😱 Fake auth header is missing! 😱")

        tokens = header.split(" ")
        if len(tokens) != 3:
            raise AuthException("🤯 Fake auth header is invalid! 🤯")

        _, org_id, roles = header.split(" ")
        self.org_id = org_id
        self.roles = roles.split(",")
    
    def to_user_restrictions(self) -> UserRestrictions:
        return UserRestrictions(org_id=self.org_id, roles=self.roles)



class DatePeriodParam(BaseModel):
    start: date
    end: date

    @model_validator(mode="after")  
    def check_start_and_end(cls, values: "DatePeriodParam") -> "DatePeriodParam":
        """ 
        Runs after all fields are validated and before the model is created. 
        Example showing multi field validation that will translate into a nice error message.

        This type of response we want to keep out of a domain layer shared with an ETL.
        """
        if values.start < values.end:
            return values
        else:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date ⌛"
            )


class UpsertMetricRequest(BaseModel):
    """ 
    Maps incoming data to most of the fields on a domain object.
    The DAL and Service will enforce that the org_id is set and that the date is unique.
    We're just making sure that no extra data gets in there.
    """
    metric_date: date
    mttr: float
    open_findings: int
    closed_findings: int

    @classmethod
    def to_model(cls, request: "UpsertMetricRequest") -> Metric:
        return Metric(
            date=request.metric_date,
            mttr=request.mttr,
            open_findings=request.open_findings,
            closed_findings=request.closed_findings,
        )


class MetricComparisonResponse(BaseModel):
    current_value: str
    past_value: str
    percent_change: str

    @classmethod
    def from_model(cls, current: Metric, past: Metric, selector: MetricSelector):
        """ Shows off doing mapping logic directly on the mapping logic object. """
        current_value = selector(current)
        past_value = selector(past)
        change = "NaN" if current_value == 0 else int(past_value / current_value * 100)
        return cls(
            current_value=str(current_value),
            past_value=str(past_value),
            percent_change=str(change),
        )


class MetricChartResponse(BaseModel):
    """ Mapping nested objects is also a thing. """
    class ChartValues(BaseModel):
        label: str
        value: float

    values: List[ChartValues]

    @classmethod
    def from_model(cls, metrics: List[Metric], selector: MetricSelector):
        values = [
            cls.ChartValues(
                label=str(metric.date),
                value=selector(metric),
            )
            for metric in metrics
        ]
        return cls(values=values)
