"""Main FastAPI application entrypoint."""

from fastapi import FastAPI, HTTPException
import httpx

from config import settings
from models import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    NobitexBalance,
    OrderRequest,
    OrderResponse,
    PayoutRequest,
    PayoutResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)
import nobitex_client
import payping_client

app = FastAPI(title="IRR to USDT Swap")


@app.post("/payping/create", response_model=CreatePaymentResponse)
async def create_payment(req: CreatePaymentRequest) -> CreatePaymentResponse:
    """Create a payment using PayPing."""

    try:
        return await payping_client.create_payment(req)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/payping/verify", response_model=VerifyPaymentResponse)
async def verify_payment(req: VerifyPaymentRequest) -> VerifyPaymentResponse:
    """Verify a PayPing payment."""

    try:
        return await payping_client.verify_payment(req)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/payping/payout", response_model=PayoutResponse)
async def create_payout(req: PayoutRequest) -> PayoutResponse:
    """Create a payout via PayPing."""

    try:
        return await payping_client.create_payout(req)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/nobitex/balance", response_model=NobitexBalance)
async def get_balance() -> NobitexBalance:
    """Retrieve balances from Nobitex."""

    try:
        return await nobitex_client.get_balance()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/nobitex/order", response_model=OrderResponse)
async def place_order(req: OrderRequest) -> OrderResponse:
    """Place an order on Nobitex."""

    try:
        return await nobitex_client.place_order(req)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/webhooks/payping")
async def payping_webhook(req: VerifyPaymentRequest):
    """Handle PayPing webhook by verifying and paying out to Nobitex."""

    try:
        verify_resp = await payping_client.verify_payment(req)
        payout_req = PayoutRequest(
            sheba=settings.nobitex_sheba,
            amount=verify_resp.amount,
            description=f"Webhook payout for {req.code}",
        )
        payout_resp = await payping_client.create_payout(payout_req)
        return {
            "status": "processed",
            "payment": verify_resp.dict(),
            "payout": payout_resp.dict(),
        }
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
