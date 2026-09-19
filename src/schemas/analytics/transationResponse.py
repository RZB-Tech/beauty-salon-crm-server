from pydantic import BaseModel
from datetime import date

from src.schemas.base import MoneyResponse

class PaymentMethodsAnalyticsDetailsResponse(BaseModel):
    amount: MoneyResponse
    profit: MoneyResponse
    percentage: MoneyResponse

class PaymentMethodsAnalyticsResponse(BaseModel):
    cash: PaymentMethodsAnalyticsDetailsResponse
    card: PaymentMethodsAnalyticsDetailsResponse
    deposit: PaymentMethodsAnalyticsDetailsResponse
    gift_card: PaymentMethodsAnalyticsDetailsResponse

class TransactionAnalyticsResponse(BaseModel):
    payment_methods: PaymentMethodsAnalyticsResponse
    by_service: PaymentMethodsAnalyticsDetailsResponse
    by_material: PaymentMethodsAnalyticsDetailsResponse
    by_giftCard: PaymentMethodsAnalyticsDetailsResponse
    not_fully_paid_receipts_sum: MoneyResponse
    total_profit: MoneyResponse

class TransactionByPeriodBaseResponse(BaseModel):
    date: date
    revenue: MoneyResponse

class TransactionByPeriodResponse(BaseModel):
    items: list[TransactionByPeriodBaseResponse]