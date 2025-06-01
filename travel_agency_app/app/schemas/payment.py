from typing import Optional, Dict, Any # Added Dict, Any
from datetime import datetime
from decimal import Decimal
from .base import BaseSchema, TimestampedSchema

class PaymentIntentCreateRequest(BaseSchema):
    booking_id: int
    # Amount might be derived from booking_id in the service, or passed explicitly
    # currency: str = "usd" # Often fixed or derived

class PaymentIntentResponse(BaseSchema):
    client_secret: str
    payment_intent_id: str
    booking_id: int
    amount: Decimal # The amount processed by the payment intent
    currency: str

# Existing Payment Schemas (can remain for internal DB representation)
class PaymentBase(BaseSchema):
    booking_id: int
    amount: Decimal
    payment_method: Optional[str] = "stripe"
    transaction_id: Optional[str] = None # Stripe Payment Intent ID can go here
    status: str = 'Pending' # Initial status before Stripe confirmation

class PaymentCreate(PaymentBase):
    # This might be used internally after Stripe confirms payment via webhook
    pass

class PaymentUpdate(BaseSchema):
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    status: Optional[str] = None

class PaymentRead(PaymentBase, TimestampedSchema):
    payment_date: datetime
