from pydantic import BaseModel

class PaymentMethodsAnalyticsDetailsResponse(BaseModel):
    amount: int
    profit: int
    percentage: float

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
    total_profit: int