from typing import List

from pydantic import BaseModel


class MonthlyQuoteMetric(BaseModel):
    month: str
    quotes: int


class ServiceDemandMetric(BaseModel):
    name: str
    value: int


class CustomerTypeMetric(BaseModel):
    name: str
    value: int


class TopDestinationMetric(BaseModel):
    destination: str
    requests: int


class AnalyticsSummary(BaseModel):
    totalQuotes: int
    quotesThisMonth: int
    topService: str
    topDestination: str
    monthlyQuotes: List[MonthlyQuoteMetric]
    serviceDemand: List[ServiceDemandMetric]
    customerTypes: List[CustomerTypeMetric]
    topDestinations: List[TopDestinationMetric]