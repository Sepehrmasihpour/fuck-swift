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
    """
    Handle PayPing payment callback:
      1. Verify the incoming IRR payment.
      2. Create a payout to Nobitex’s Sheba (IRR deposit).
      3. Place a market_sell order on Nobitex (IRT→USDT).
    """
    try:
        # 1) Verify payment
        verify_resp = await payping_client.verify_payment(req)

        # 2) Disburse IRR into Nobitex
        payout_req = PayoutRequest(
            sheba=settings.nobitex_sheba,
            amount=verify_resp.amount,
            description=f"Webhook payout for PayPing code={req.code}",
        )
        payout_resp = await payping_client.create_payout(payout_req)

        # 3) Place IRT→USDT market sell order
        order_req = OrderRequest(
            symbol="IRT-USDT", type="market_sell", amount=verify_resp.amount
        )
        order_resp = await nobitex_client.place_order(order_req)

        return {
            "status": "processed",
            "payment": verify_resp,
            "payout": payout_resp,
            "order": order_resp,
        }

    except httpx.HTTPError as exc:
        # Network or API error
        raise HTTPException(
            status_code=502, detail=f"External API error: {exc}"
        ) from exc
    except Exception as exc:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=500, detail=f"Internal processing error: {exc}"
        ) from exc
