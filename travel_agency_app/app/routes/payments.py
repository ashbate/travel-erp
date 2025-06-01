import stripe # Add import
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models
from app.services.payment_service import PaymentService
from app.database import get_db
from app.core.config import settings

router = APIRouter()

def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(db_session=db)

@router.post("/create-payment-intent", response_model=schemas.PaymentIntentResponse)
async def create_payment_intent_endpoint(
    intent_request: schemas.PaymentIntentCreateRequest,
    service: PaymentService = Depends(get_payment_service)
):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe payments are not configured.")
    try:
        intent_details = await service.create_payment_intent(intent_request=intent_request)
        return schemas.PaymentIntentResponse(**intent_details)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the exception
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not process payment intent.")

@router.post("/stripe-webhooks")
async def stripe_webhooks_endpoint(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    service: PaymentService = Depends(get_payment_service)
):
    if not settings.STRIPE_WEBHOOK_SECRET:
        print("Warning: STRIPE_WEBHOOK_SECRET is not set. Cannot verify webhook.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook secret not configured.")

    payload = await request.body()
    try:
        event = await stripe.Webhook.construct_event_async( # Async construction
            payload, sig_header=stripe_signature, secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e: # Invalid payload
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payload: {e}")
    except stripe.error.SignatureVerificationError as e: # Invalid signature
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid signature: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Webhook error: {e}")

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object # contains a stripe.PaymentIntent
        booking_id = payment_intent.metadata.get('booking_id')
        if booking_id:
            try:
                service.record_stripe_payment(
                    booking_id=int(booking_id),
                    payment_intent_id=payment_intent.id,
                    amount=Decimal(payment_intent.amount_received), # amount_received is in cents
                    status='Succeeded',
                    currency=payment_intent.currency
                )
            except ValueError as e:
                # Log error, e.g. booking not found or other issue
                print(f"Error processing successful payment webhook: {e} for PI {payment_intent.id}")
                # Return 200 to Stripe anyway so it doesn't keep retrying for this specific error
                # but log it for investigation.
                return {"status": "error processing event but acknowledged"}
        else:
            print(f"Webhook for PI Succeeded {payment_intent.id} missing booking_id in metadata.")

    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        booking_id = payment_intent.metadata.get('booking_id')
        if booking_id:
            try:
                service.record_stripe_payment(
                    booking_id=int(booking_id),
                    payment_intent_id=payment_intent.id,
                    amount=Decimal(payment_intent.amount), # amount is in cents
                    status='Failed',
                    currency=payment_intent.currency
                )
            except ValueError as e:
                print(f"Error processing failed payment webhook: {e} for PI {payment_intent.id}")
                return {"status": "error processing event but acknowledged"}
        else:
            print(f"Webhook for PI Failed {payment_intent.id} missing booking_id in metadata.")
    else:
        print(f"Unhandled event type {event.type}")

    return {"status": "success"}


# Existing endpoints (get_payments_for_booking, get_payment, update_payment_status_endpoint)
# The create_payment endpoint is replaced by create_payment_intent_endpoint.
# The update_payment_status_endpoint might be less relevant if Stripe webhooks are the source of truth.

@router.get("/booking/{booking_id}", response_model=List[schemas.PaymentRead])
# ... (no changes to this existing endpoint)
async def read_payments_for_booking(
    booking_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    return service.get_payments_for_booking(booking_id=booking_id)

@router.get("/{payment_id}", response_model=schemas.PaymentRead)
# ... (no changes to this existing endpoint)
async def read_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    db_payment = service.get_payment_by_id(payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return db_payment

@router.put("/{payment_id}/status", response_model=schemas.PaymentRead)
# ... (no changes to this existing endpoint, but consider its role)
async def update_payment_status_endpoint(
    payment_id: int,
    status_update: schemas.PaymentUpdate,
    service: PaymentService = Depends(get_payment_service)
):
    if status_update.status is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status field is required.")
    try:
        updated_payment = service.update_payment_status(
            payment_id=payment_id,
            status=status_update.status,
            transaction_id=status_update.transaction_id
        )
        if updated_payment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return updated_payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
