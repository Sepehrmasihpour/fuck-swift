# Agent Overview

This document describes the **IRR → USDT Orchestrator Agent**, a FastAPI-based service that automates real-money rial (IRR) collection via PayPing, on-chain stablecoin withdrawals, and fiat trades on Nobitex.

---

## 1. Purpose

The Agent centralizes and automates the following flows:

1. **Inbound IRR Payments**

   - Create PayPing payment links or invoices.
   - Receive real-time webhooks when customers pay in IRR.

2. **IRR Disbursement**

   - Push received IRR from the PayPing wallet to the Nobitex exchange via PayPing Payouts.

3. **Crypto Trading**

   - Poll Nobitex for IRR balance updates.
   - Execute IRR→USDT market sell orders.
   - (Optional) Withdraw USDT on-chain via API.

4. **Status Tracking & Notifications**

   - Expose API endpoints for clients to query deposit and payout statuses.
   - Push webhooks for key events (payment verified, payout completed, order filled).

---

## 2. Architecture

```plaintext
+-------------+     PayPing API      +-------------+     Nobitex API     +-----------+
|  Web Client | ── create payment ──> |  Agent      | ── place order ──> |  Nobitex  |
+-------------+                       +-------------+                     +-----------+
         ^                                     |                                |
         |                                     v                                v
         |<── webhook & status updates ─────┐    └─ poll balance & track ─────┐
+-------------+                            |                                 |
| Callback    |                            v                                 |
| Endpoint    |                       Disburse IRR via PayPing Payouts        |
+-------------+                                                              |
                                                                             v
                                                                      +-------------+
                                                                      | Blockchain  |
                                                                      | On-chain    |
                                                                      +-------------+
```

---

## 3. Components

| Module              | Responsibility                              |
| ------------------- | ------------------------------------------- |
| `main.py`           | Application entrypoint, router registration |
| `config.py`         | Environment variable loading (`dotenv`)     |
| `models.py`         | Pydantic models for requests & responses    |
| `payping_client.py` | OAuth2 flow, create payment, verify, payout |
| `nobitex_client.py` | Balance query, trade placement, withdrawal  |
| `webhooks.py`       | Handlers for PayPing callbacks              |
| `tasks.py`          | Background polls, retries, reconciliation   |

---

## 4. Configuration & Environment

Define the following in `.env`:

```ini
# PayPing
PAYPING_CLIENT_ID=your-client-id
PAYPING_CLIENT_SECRET=your-client-secret
# Nobitex
NOBITEX_API_KEY=your-api-key
NOBITEX_BASE_URL=https://api.nobitex.ir
# (Optional) Tron/Ethereum RPC
RPC_URL=https://...
HOT_WALLET_ADDRESS=0x...
HOT_WALLET_PRIVATE_KEY=...
```

---

## 5. API Endpoints

### PayPing Flow

- `POST /payping/create`
  Create a new payment link.
  **Request:** `{ amount_irr, order_id, callback_url }`
  **Response:** `{ code, payment_url }`

- `POST /payping/verify`
  Confirm a payment by code.
  **Request:** `{ code }`
  **Response:** `{ status, amount }`

- `POST /payping/payout`
  Disburse IRR to Nobitex Sheba.
  **Request:** `{ sheba, amount, description }`
  **Response:** `{ payout_id, status }`

### Nobitex Flow

- `GET /nobitex/balance`
  Returns IRR & USDT balances.

- `POST /nobitex/order`
  Place a market sell order.
  **Request:** `{ symbol, type, amount }`
  **Response:** `{ order_id, status, filled_amount }`

- `POST /nobitex/withdraw` (optional)
  Withdraw USDT on-chain.
  **Request:** `{ to_address, amount }`
  **Response:** `{ tx_hash, status }`

---

## 6. Workflow

1. **Client** calls `/payping/create` → redirects user to PayPing payment.
2. **PayPing** calls `POST /webhooks/payping` on your Agent with `{ code }`.
3. Agent calls `verify_payment(code)` → obtains `{ amount }`.
4. Agent immediately calls `create_payout(nobitex_sheba, amount, desc)`.
5. Agent returns 200 to PayPing and stores `{ payout_id }`.
6. In background, Agent **polls** `/nobitex/balance`.

   - If IRR increased → call `/nobitex/order` to sell all IRR for USDT.
   - Optionally, withdraw USDT via `/nobitex/withdraw`.

7. Agent exposes status via its public API for client dashboards.

---

## 7. Error Handling & Retries

- Use **exponential backoff** for HTTP calls.
- Persist failed `payout_id` & `order_id` with retry counters.
- Alert on repeated failures via logs or notification channel.

---

## 8. Deployment & Monitoring

- **Containerize** with Docker: run Uvicorn.
- Use **Heroku/Vercel** or an Iranian-hosted VPS.
- Set up **Prometheus/Grafana** or simple uptime checks.
- Configure **log aggregation** (e.g. Elastic Stack).

---

_End of Agent Documentation._
