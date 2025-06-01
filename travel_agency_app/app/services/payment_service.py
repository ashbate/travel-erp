import stripe
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from decimal import Decimal

from app import models
from app import schemas
from app.services.booking_service import BookingService
from app.core.config import settings

class PaymentService:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.booking_service = BookingService(db_session)
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
        else:
            print("Warning: STRIPE_SECRET_KEY not found. Stripe functionality will be disabled or use mocks.")

    async def create_payment_intent(self, intent_request: schemas.PaymentIntentCreateRequest) -> Dict[str, Any]:
        if not settings.STRIPE_SECRET_KEY:
            # Mock response or raise error if Stripe is not configured
            return {
                "client_secret": "mock_client_secret_for_testing",
                "payment_intent_id": "pi_mock_intent",
                "booking_id": intent_request.booking_id,
                "amount": Decimal("0.00"), # Placeholder, fetch actual booking amount
                "currency": "usd"
            }

        db_booking = self.booking_service.get_booking_by_id(intent_request.booking_id)
        if not db_booking:
            raise ValueError("Booking not found.")
        if db_booking.status == 'Paid':
            raise ValueError("Booking is already paid.")
        if db_booking.total_price <= 0:
            raise ValueError("Booking total price must be positive to create a payment intent.")

        try:
            # Amount must be in cents for Stripe
            amount_in_cents = int(db_booking.total_price * 100)

            payment_intent_params = {
                'amount': amount_in_cents,
                'currency': 'usd', # Or make this configurable
                'metadata': {'booking_id': db_booking.id, 'guest_id': db_booking.guest_id},
                # Add other parameters like 'customer' if you manage Stripe customers
            }

            intent = await stripe.PaymentIntent.create_async(**payment_intent_params) # Async call

            # Optionally, create a preliminary Payment record in your DB now with 'Pending' status
            # This helps track initiated payments even if not completed by user.
            # For this example, we'll assume a Payment record is created/updated via webhook.

            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "booking_id": db_booking.id,
                "amount": db_booking.total_price, # Original decimal amount
                "currency": intent.currency
            }
        except stripe.StripeError as e:
            print(f"Stripe API error: {e}")
            raise ValueError(f"Stripe error: {e.user_message}") # Provide user-friendly message if available
        except Exception as e:
            print(f"Error creating payment intent: {e}")
            raise ValueError("Could not create payment intent.")

    # --- Existing methods (get_payment_by_id, etc.) can remain for internal use or webhook handling ---
    def get_payment_by_id(self, payment_id: int) -> Optional[models.Payment]:
        return self.db.query(models.Payment).filter(models.Payment.id == payment_id).first()

    def get_payments_for_booking(self, booking_id: int) -> List[models.Payment]:
        return self.db.query(models.Payment).filter(models.Payment.booking_id == booking_id).all()

    # This method will be primarily driven by webhooks from Stripe
    def record_stripe_payment(self, booking_id: int, payment_intent_id: str, amount: Decimal, status: str, currency: str = 'usd') -> models.Payment:
        db_booking = self.booking_service.get_booking_by_id(booking_id)
        if not db_booking:
            # This should ideally not happen if metadata from Stripe is correct
            raise ValueError("Booking not found for this payment recording.")

        # Check if a payment record for this intent already exists
        db_payment = self.db.query(models.Payment).filter(models.Payment.transaction_id == payment_intent_id).first()

        if not db_payment:
            db_payment = models.Payment(
                booking_id=booking_id,
                amount=amount / 100 if currency.lower() in ['usd', 'eur', 'gbp'] else amount, # Adjust if amount from Stripe is in cents
                payment_method="stripe",
                transaction_id=payment_intent_id,
                status=status # e.g., 'Succeeded', 'Failed'
            )
            self.db.add(db_payment)
        else:
            db_payment.status = status
            db_payment.amount = amount / 100 if currency.lower() in ['usd', 'eur', 'gbp'] else amount
            self.db.add(db_payment)

        self.db.commit()
        self.db.refresh(db_payment)

        # Update booking status based on payment
        if status.lower() == 'succeeded':
            current_paid_amount = sum(p.amount for p in self.get_payments_for_booking(booking_id) if p.status.lower() == 'succeeded')
            if current_paid_amount >= db_booking.total_price:
                self.booking_service.update_booking_status(db_booking.id, "Paid")
            else:
                self.booking_service.update_booking_status(db_booking.id, "Confirmed") # Or 'PartiallyPaid'
        elif status.lower() == 'failed':
            # Handle failed payment, maybe set booking status to 'PaymentFailed'
            if db_booking.status not in ["Cancelled", "Paid"]:
                 self.booking_service.update_booking_status(db_booking.id, "PaymentFailed")
        return db_payment

    # update_payment_status: This might be deprecated or used for manual admin changes if Stripe is source of truth
    # For now, let's assume it's still usable for manual overrides if needed.
    def update_payment_status(self, payment_id: int, status: str, transaction_id: Optional[str] = None) -> Optional[models.Payment]:
        # ... (existing logic, but consider if it conflicts with webhook updates) ...
        db_payment = self.get_payment_by_id(payment_id)
        if not db_payment:
            return None

        db_payment.status = status
        if transaction_id:
            db_payment.transaction_id = transaction_id

        self.db.add(db_payment)
        self.db.commit()
        self.db.refresh(db_payment)
        # Re-evaluate booking status (copied from original method)
        db_booking = self.booking_service.get_booking_by_id(db_payment.booking_id)
        if db_booking:
            if status.lower() == 'succeeded':
                current_paid_amount = sum(p.amount for p in self.get_payments_for_booking(db_payment.booking_id) if p.status.lower() == 'succeeded')
                if current_paid_amount >= db_booking.total_price:
                    self.booking_service.update_booking_status(db_booking.id, "Paid")
                elif db_booking.status == 'Pending':
                    self.booking_service.update_booking_status(db_booking.id, "Confirmed")
            elif status.lower() in ['failed', 'refunded']:
                current_paid_amount = sum(p.amount for p in self.get_payments_for_booking(db_payment.booking_id) if p.status.lower() == 'succeeded')
                if current_paid_amount < db_booking.total_price and db_booking.status == "Paid":
                    self.booking_service.update_booking_status(db_booking.id, "Confirmed")
        return db_payment
