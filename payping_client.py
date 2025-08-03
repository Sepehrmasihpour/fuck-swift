"""Async client for interacting with the PayPing API."""
from typing import Dict

import httpx

from config import settings
from models import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    PayoutRequest,
    PayoutResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)

PAYPING_BASE_URL = "https://api.payping.ir"


async def get_access_token() -> str:
    """Retrieve an OAuth2 access token from PayPing."""

    token_url = f"{PAYPING_BASE_URL}/token"
    data = {"grant_type": "client_credentials"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data=data,
            auth=(settings.payping_client_id, settings.payping_client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json().get("access_token", "")


async def create_payment(req: CreatePaymentRequest) -> CreatePaymentResponse:
    """Create a new payment request in PayPing."""

    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload: Dict[str, str | int] = {
        "clientRefId": req.order_id,
        "amount": req.amount_irr,
        "returnUrl": str(req.callback_url),
    }

    async with httpx.AsyncClient(base_url=PAYPING_BASE_URL, headers=headers) as client:
        response = await client.post("/new/v2/pay", json=payload)
        response.raise_for_status()
        data = response.json()
        return CreatePaymentResponse(code=data.get("code", ""), payment_url=data.get("url", ""))


async def verify_payment(req: VerifyPaymentRequest) -> VerifyPaymentResponse:
    """Verify a payment with PayPing."""

    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(base_url=PAYPING_BASE_URL, headers=headers) as client:
        response = await client.post("/new/v2/pay/verify", json={"code": req.code})
        response.raise_for_status()
        data = response.json()
        return VerifyPaymentResponse(status=data.get("status", ""), amount=data.get("amount", 0))


async def create_payout(req: PayoutRequest) -> PayoutResponse:
    """Initiate a payout to a Sheba number via PayPing."""

    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "sheba": req.sheba,
        "amount": req.amount,
        "description": req.description,
    }
    async with httpx.AsyncClient(base_url=PAYPING_BASE_URL, headers=headers) as client:
        response = await client.post("/v2/payouts", json=payload)
        response.raise_for_status()
        data = response.json()
        return PayoutResponse(
            payout_id=data.get("id", ""),
            status=data.get("status", ""),
        )
