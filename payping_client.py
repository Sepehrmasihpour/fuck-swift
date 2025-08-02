"""Async client for interacting with the PayPing API.

Fill in real API endpoints and add proper error handling or retries as
required by your application.
"""

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

PAYPING_BASE_URL = "https://api.payping.ir"  # Replace with testnet URL if needed


async def get_access_token() -> str:
    """Obtain an OAuth2 access token using client credentials."""

    token_url = f"{PAYPING_BASE_URL}/token"  # TODO: confirm token endpoint
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.payping_client_id,
        "client_secret": settings.payping_client_secret,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data)
        resp.raise_for_status()  # TODO: add retry logic
        return resp.json().get("access_token", "")


async def create_payment(req: CreatePaymentRequest) -> CreatePaymentResponse:
    """Create a new payment request."""

    access_token = await get_access_token()
    url = f"{PAYPING_BASE_URL}/new/v2/pay"  # TODO: verify endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=req.dict(), headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return CreatePaymentResponse(payment_url=data.get("paymentUrl", ""), code=data.get("code", ""))


async def verify_payment(req: VerifyPaymentRequest) -> VerifyPaymentResponse:
    """Verify an existing payment."""

    access_token = await get_access_token()
    url = f"{PAYPING_BASE_URL}/new/v2/pay/verify"  # TODO: verify endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=req.dict(), headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return VerifyPaymentResponse(status=data.get("status", ""), amount=data.get("amount", 0))


async def create_payout(req: PayoutRequest) -> PayoutResponse:
    """Create a payout to a Sheba account."""

    access_token = await get_access_token()
    url = f"{PAYPING_BASE_URL}/v2/payouts"  # TODO: verify endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=req.dict(), headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return PayoutResponse(payout_id=data.get("id", ""), status=data.get("status", ""))
