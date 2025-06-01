from fastapi import APIRouter

# Import individual routers
from .tours import router as tours_router
from .bookings import router as bookings_router
from .guests import router as guests_router
from .hotels import router as hotels_router
from .users import router as users_router
from .payments import router as payments_router
from .token import router as token_router # Add this import


api_router_v1 = APIRouter()

# Include the token router *before* other routers if there's any path ambiguity,
# though for '/token' it's usually fine. Best practice often places it first or distinctly.
api_router_v1.include_router(token_router, prefix="/token", tags=["Authentication"])

api_router_v1.include_router(tours_router, prefix="/tours", tags=["Tours"])
api_router_v1.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
api_router_v1.include_router(guests_router, prefix="/guests", tags=["Guests"])
api_router_v1.include_router(hotels_router, prefix="/hotels", tags=["Hotels & Rooms"])
api_router_v1.include_router(users_router, prefix="/users", tags=["Users"])
api_router_v1.include_router(payments_router, prefix="/payments", tags=["Payments"])
