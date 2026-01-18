import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock
from service import MetricsService
from models import Metric
from dal import MetricsDAL

@pytest.fixture
def mock_repo():
    return AsyncMock(spec=MetricsDAL)

@pytest.fixture
def service(mock_repo):
    return MetricsService(repo=mock_repo)

@pytest.mark.asyncio
async def test_get_metrics_between(service, mock_repo):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 3)
    expected_dates = [start_date, start_date + timedelta(days=1), end_date]
    expected_metrics = [
        Metric(date=date(2023, 1, 1)), 
        Metric(date=date(2023, 1, 2)), 
        Metric(date=date(2023, 1, 3)), 
    ]

    mock_repo.get_metrics_for.return_value = expected_metrics

    result = await service.get_metrics_between(start_date, end_date)

    mock_repo.get_metrics_for.assert_awaited_once_with(expected_dates)
    assert result == expected_metrics

@pytest.mark.asyncio
async def test_get_metrics_for(service, mock_repo):
    dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
    expected_metrics = [
        Metric(date=date(2023, 1, 1)), 
        Metric(date=date(2023, 1, 2)), 
        Metric(date=date(2023, 1, 3)), 
    ]

    mock_repo.get_metrics_for.return_value = expected_metrics

    result = await service.get_metrics_for(dates)

    mock_repo.get_metrics_for.assert_awaited_once_with(dates)
    assert result == expected_metrics

def test_dates_between(service):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 3)
    expected_dates = [start_date, start_date + timedelta(days=1), end_date]

    result = service.dates_between(start_date, end_date)

    assert result == expected_dates