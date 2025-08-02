"""Pydantic models for PayPing and Nobitex interactions."""

from pydantic import BaseModel


class CreatePaymentRequest(BaseModel):
    amount_irr: int
    order_id: str
    callback_url: str


class CreatePaymentResponse(BaseModel):
    payment_url: str
    code: str


class VerifyPaymentRequest(BaseModel):
    code: str


class VerifyPaymentResponse(BaseModel):
    status: str
    amount: int


class PayoutRequest(BaseModel):
    sheba: str
    amount: int
    description: str


class PayoutResponse(BaseModel):
    payout_id: str
    status: str
