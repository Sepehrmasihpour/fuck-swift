"""Pydantic data models used across the application."""
from typing import Dict

from pydantic import BaseModel, HttpUrl


class CreatePaymentRequest(BaseModel):
    """Request payload for creating a PayPing payment."""

    order_id: str
    amount_irr: int
    callback_url: HttpUrl


class CreatePaymentResponse(BaseModel):
    """Response returned after creating a PayPing payment."""

    code: str
    payment_url: HttpUrl


class VerifyPaymentRequest(BaseModel):
    """Request payload for verifying a PayPing payment."""

    code: str


class VerifyPaymentResponse(BaseModel):
    """Response returned after verifying a PayPing payment."""

    status: str
    amount: int


class PayoutRequest(BaseModel):
    """Request payload for creating a payout via PayPing."""

    sheba: str
    amount: int
    description: str


class PayoutResponse(BaseModel):
    """Response returned after creating a PayPing payout."""

    payout_id: str
    status: str


class NobitexBalance(BaseModel):
    """Model representing balance information from Nobitex."""

    assets: Dict[str, float]


class OrderRequest(BaseModel):
    """Request payload for placing an order on Nobitex."""

    symbol: str
    type: str
    amount: int


class OrderResponse(BaseModel):
    """Response returned after placing an order on Nobitex."""

    order_id: str
    status: str
    filled: float
