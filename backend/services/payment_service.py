from __future__ import annotations

from datetime import datetime
import hashlib
import hmac
import os
import uuid

import bcrypt


def get_razorpay_key_id() -> str:
    return os.getenv('RAZORPAY_KEY_ID', 'rzp_test_placeholder')


def get_razorpay_key_secret() -> str:
    return os.getenv('RAZORPAY_KEY_SECRET', 'test_secret_placeholder')


def verify_razorpay_signature(razorpay_order_id: str, razorpay_payment_id: str, signature: str | None) -> bool:
    payload = f'{razorpay_order_id}|{razorpay_payment_id}'.encode('utf-8')
    expected = hmac.new(get_razorpay_key_secret().encode('utf-8'), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or '')


def create_razorpay_order(amount: int, receipt: str) -> dict:
    try:
        import razorpay

        client = razorpay.Client(auth=(get_razorpay_key_id(), get_razorpay_key_secret()))
        return client.order.create({
            'amount': amount,
            'currency': 'INR',
            'receipt': receipt,
            'payment_capture': 1,
        })
    except Exception:
        return {
            'id': f'order_dev_{uuid.uuid4().hex[:16]}',
            'amount': amount,
            'currency': 'INR',
            'receipt': receipt,
        }


def issue_refund(payment_id: str) -> None:
    import razorpay

    client = razorpay.Client(auth=(get_razorpay_key_id(), get_razorpay_key_secret()))
    client.payment.refund(payment_id)


def normalize_card_number(card_number: str) -> str:
    return ''.join(ch for ch in (card_number or '') if ch.isdigit())


def is_valid_luhn(card_number: str) -> bool:
    digits = normalize_card_number(card_number)
    if len(digits) < 12:
        return False

    checksum = 0
    reverse_digits = digits[::-1]
    for index, char in enumerate(reverse_digits):
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
        month = int(month_str)
        year = int(year_str)
        if month < 1 or month > 12:
            return False
        now = datetime.utcnow()
        if year < now.year:
            return False
        if year == now.year and month < now.month:
            return False
        return True
    except Exception:
        return False
