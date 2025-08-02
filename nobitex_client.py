"""Async wrapper around the Nobitex API.

Replace placeholder endpoints with actual ones and implement proper
error handling or retry logic as needed.
"""

import httpx

from config import settings


async def get_balance() -> dict:
    """Retrieve account balances from Nobitex."""

    url = f"{settings.nobitex_base_url}/v1/balance"  # TODO: verify endpoint
    headers = {"Authorization": settings.nobitex_api_key}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()


async def place_order(symbol: str, order_type: str, amount: int) -> dict:
    """Place a new order on Nobitex."""

    url = f"{settings.nobitex_base_url}/v1/orders"  # TODO: verify endpoint
    headers = {"Authorization": settings.nobitex_api_key}
    payload = {"symbol": symbol, "type": order_type, "amount": amount}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


async def withdraw_usdt(to_address: str, amount: float) -> dict:
    """Withdraw USDT to an external address (optional)."""

    url = f"{settings.nobitex_base_url}/v1/withdraw"  # TODO: verify endpoint
    headers = {"Authorization": settings.nobitex_api_key}
    payload = {"address": to_address, "amount": amount}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
