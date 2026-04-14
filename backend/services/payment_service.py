from __future__ import annotations

# ---------------------------------------------------------------------------
# PAYMENT SERVICE
# Razorpay integration is commented out.  All functions return realistic mock
# responses so the rest of the app works exactly as if a real gateway were
# connected.  To re-enable Razorpay:
#   1. pip install razorpay  (already in requirements.txt)
#   2. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env
#   3. Uncomment the blocks marked  ## RAZORPAY ##
# ---------------------------------------------------------------------------

from datetime import datetime
import hashlib
import hmac
import os
import uuid

import bcrypt


# ---------------------------------------------------------------------------
# Key helpers
# ---------------------------------------------------------------------------

def get_razorpay_key_id() -> str:
    return os.getenv('RAZORPAY_KEY_ID', 'rzp_test_mock_key')


def get_razorpay_key_secret() -> str:
    return os.getenv('RAZORPAY_KEY_SECRET', 'mock_secret')


# ---------------------------------------------------------------------------
# Signature verification  (mock always passes; real check is commented out)
# ---------------------------------------------------------------------------

def verify_razorpay_signature(razorpay_order_id: str, razorpay_payment_id: str, signature: str | None) -> bool:
    if not signature:
        return False

    ## RAZORPAY ## — uncomment to verify real webhook signatures
    # payload = f'{razorpay_order_id}|{razorpay_payment_id}'.encode('utf-8')
    # expected = hmac.new(get_razorpay_key_secret().encode('utf-8'), payload, hashlib.sha256).hexdigest()
    # return hmac.compare_digest(expected, signature)

    # Mock: any non-empty signature is accepted
    return True


# ---------------------------------------------------------------------------
# Order creation  (mock returns a realistic order dict)
# ---------------------------------------------------------------------------

def create_razorpay_order(amount: int, receipt: str) -> dict:
    ## RAZORPAY ## — uncomment to create real Razorpay orders
    # import razorpay
    # client = razorpay.Client(auth=(get_razorpay_key_id(), get_razorpay_key_secret()))
    # return client.order.create({
    #     'amount': amount,
    #     'currency': 'INR',
    #     'receipt': receipt,
    #     'payment_capture': 1,
    # })

    return {
        'id': f'order_mock_{uuid.uuid4().hex[:16]}',
        'amount': amount,
        'currency': 'INR',
        'receipt': receipt,
        'status': 'created',
    }


# ---------------------------------------------------------------------------
# Refund  (mock is a no-op)
# ---------------------------------------------------------------------------

def issue_refund(payment_id: str) -> None:
    ## RAZORPAY ## — uncomment to issue real refunds
    # import razorpay
    # client = razorpay.Client(auth=(get_razorpay_key_id(), get_razorpay_key_secret()))
    # client.payment.refund(payment_id)

    # Mock: log and return silently
    print(f'[mock] Refund issued for payment {payment_id}')


# ---------------------------------------------------------------------------
# Card utilities  (these are real — no Razorpay dependency)
# ---------------------------------------------------------------------------

def normalize_card_number(card_number: str) -> str:
    return ''.join(ch for ch in (card_number or '') if ch.isdigit())


def is_valid_luhn(card_number: str) -> bool:
    digits = normalize_card_number(card_number)
    if len(digits) < 12:
        return False
    checksum = 0
    for index, char in enumerate(reversed(digits)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        checksum += value
    return checksum % 10 == 0


def hash_card_number(card_number: str) -> str:
    normalized = normalize_card_number(card_number)
    return bcrypt.hashpw(normalized.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def validate_card_expiry(card_expiry: str) -> bool:
    try:
        month_str, year_str = (card_expiry or '').split('/')
        month, year = int(month_str), int(year_str)
        if month < 1 or month > 12:
            return False
        now = datetime.utcnow()
        if year < now.year or (year == now.year and month < now.month):
            return False
        return True
    except Exception:
        return False
