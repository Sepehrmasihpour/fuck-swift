"""FastAPI application wiring PayPing and Nobitex clients."""

from fastapi import APIRouter, FastAPI

from config import settings
from models import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    PayoutRequest,
    PayoutResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)
from payping_client import create_payment, create_payout, verify_payment
from nobitex_client import get_balance, place_order

app = FastAPI(title="IRR to USDT Pipeline")


@app.on_event("startup")
async def startup() -> None:
    """Ensure settings are loaded at startup."""

    _ = settings


# Routers
payping_router = APIRouter(prefix="/payping", tags=["payping"])
nobitex_router = APIRouter(prefix="/nobitex", tags=["nobitex"])


@payping_router.post("/create", response_model=CreatePaymentResponse)
async def payping_create(req: CreatePaymentRequest) -> CreatePaymentResponse:
    """Create a PayPing payment."""

    return await create_payment(req)


@payping_router.post("/verify", response_model=VerifyPaymentResponse)
async def payping_verify(req: VerifyPaymentRequest) -> VerifyPaymentResponse:
    """Verify a PayPing payment."""

    return await verify_payment(req)


@payping_router.post("/payout", response_model=PayoutResponse)
async def payping_payout(req: PayoutRequest) -> PayoutResponse:
    """Initiate a payout through PayPing."""

    return await create_payout(req)


@nobitex_router.get("/balance")
async def nobitex_balance() -> dict:
    """Get Nobitex account balance."""

    return await get_balance()


@nobitex_router.post("/order")
async def nobitex_order(symbol: str, order_type: str, amount: int) -> dict:
    """Place an order on Nobitex."""

    return await place_order(symbol, order_type, amount)


@app.post("/webhooks/payping")
async def payping_webhook(payload: VerifyPaymentRequest) -> dict:
    """Handle PayPing webhook callbacks."""

    # 1. Verify the payment
    verification = await verify_payment(payload)

    # 2. Payout to Nobitex's Sheba
    payout_request = PayoutRequest(
        sheba="NOBITEX_SHEBA",  # TODO: replace with actual Sheba
        amount=verification.amount,
        description="Automatic payout",
    )
    payout_response = await create_payout(payout_request)

    # 3. Return summary
    return {"verification": verification.dict(), "payout": payout_response.dict()}


# Mount routers
app.include_router(payping_router)
app.include_router(nobitex_router)
