"""Async client for interacting with the Nobitex API."""

import httpx

from config import settings
from models import NobitexBalance, OrderRequest, OrderResponse


async def get_balance() -> NobitexBalance:
    """Retrieve account balances from Nobitex."""

    headers = {"Authorization": f"Token {settings.nobitex_api_key}"}
    async with httpx.AsyncClient(
        base_url=settings.nobitex_base_url, headers=headers
    ) as client:
        response = await client.get("/v1/balance")
        response.raise_for_status()
        data = response.json()
        assets = {k: float(v) for k, v in data.get("assets", {}).items()}
        return NobitexBalance(assets=assets)


async def place_order(req: OrderRequest) -> OrderResponse:
    """Place a new order on Nobitex."""

    headers = {"Authorization": f"Token {settings.nobitex_api_key}"}
    async with httpx.AsyncClient(
        base_url=settings.nobitex_base_url, headers=headers
    ) as client:
        response = await client.post("/v1/orders", json=req.dict())
        response.raise_for_status()
        data = response.json()
        return OrderResponse(
            order_id=str(data.get("id", "")),
            status=data.get("status", ""),
            filled=float(data.get("filled", 0)),
        )


async def withdraw_usdt(to_address: str, amount: float) -> dict:
    """Withdraw USDT to an external address."""

    headers = {"Authorization": f"Token {settings.nobitex_api_key}"}
    payload = {"currency": "usdt", "address": to_address, "amount": amount}
    async with httpx.AsyncClient(
        base_url=settings.nobitex_base_url, headers=headers
    ) as client:
        response = await client.post("/v1/withdrawals", json=payload)
        response.raise_for_status()
        return response.json()
