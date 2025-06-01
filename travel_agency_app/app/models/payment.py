from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import TimestampedModel

class Payment(TimestampedModel):
    __tablename__ = "payments"

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    payment_date = Column(DateTime, default=func.now(), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String) # e.g., 'Credit Card', 'Stripe_TXN_ID'
    transaction_id = Column(String, unique=True, index=True)
    status = Column(String, nullable=False) # e.g., 'Succeeded', 'Failed', 'Pending', 'Refunded'

    booking = relationship("Booking", back_populates="payments")
