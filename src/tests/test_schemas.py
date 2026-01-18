from datetime import date
from schemas import DatePeriodParam, MetricComparisonResponse, MetricChartResponse
from models import Metric

def test_date_period_param():
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 3)
    param = DatePeriodParam(start=start_date, end=end_date)
    
    assert param.start == start_date
    assert param.end == end_date

def test_metric_comparison_response():
    def selector(metric):
        return metric.mttr

    current_metric = Metric(date=date(2023, 1, 1), mttr=1.2)
    past_metric = Metric(date=date(2022, 1, 1), mttr=0.6)
    response = MetricComparisonResponse.from_model(
        current=current_metric,
        past=past_metric,
        selector=selector
    )

    assert response.current_value == "1.2"
    assert response.past_value == "0.6"
    assert response.percent_change == "50"

def test_metric_comparison_div0_response():
    def selector(metric):
        return metric.mttr

    current_metric = Metric(date=date(2023, 1, 1), mttr=0)
    past_metric = Metric(date=date(2022, 1, 1), mttr=6)
    response = MetricComparisonResponse.from_model(
        current=current_metric,
        past=past_metric,
        selector=selector
    )

    assert response.current_value == "0"
    assert response.past_value == "6"
    assert response.percent_change == "NaN"

def test_metric_chart_response():
    def selector(metric):
        return metric.open_findings

    metrics = [
        Metric(date=date(2023, 1, 1), open_findings=100),
        Metric(date=date(2023, 1, 2), open_findings=200),
        Metric(date=date(2023, 1, 3), open_findings=300)
    ]
    response = MetricChartResponse.from_model(metrics=metrics, selector=selector)

    assert len(response.values) == 3
    assert response.values[0].label == "2023-01-01"
    assert response.values[0].value == 100
    assert response.values[1].label == "2023-01-02"
    assert response.values[1].value == 200
    assert response.values[2].label == "2023-01-03"
    assert response.values[2].value == 300