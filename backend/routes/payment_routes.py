from datetime import datetime, timedelta
import re
import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.models import db, Order, Payment, User, SavedPaymentMethod
from backend.services.notification_service import notify_runners_new_order
from backend.services.payment_service import (
    hash_card_number,
    is_valid_luhn,
    normalize_card_number,
    validate_card_expiry,
    verify_razorpay_signature,
    create_razorpay_order,
    get_razorpay_key_id,
    issue_refund,
)

payment_bp = Blueprint('payment', __name__)

UPI_REGEX = re.compile(r'^[\w.\-]{3,}@[\w]{3,}$')
CARD_PIN_REGEX = re.compile(r'^\d{4,6}$')


def _get_user_order(order_id: str, user_id: str) -> Order | None:
    order = Order.query.get(order_id)
    if not order or order.customer_id != user_id:
        return None
    return order


def _rate_limit_payment_attempts(user_id: str) -> bool:
    cutoff = datetime.utcnow() - timedelta(minutes=10)
    return Payment.query.filter(
        Payment.user_id == user_id,
        Payment.created_at >= cutoff,
    ).count() < 5


def _err(message: str, status: int = 400):
    return jsonify({'error': message, 'message': message}), status


def _mock_order_id() -> str:
    return f'order_mock_{uuid.uuid4().hex[:16]}'


def _mock_payment_id() -> str:
    return f'pay_mock_{uuid.uuid4().hex[:12]}'


# ---------------------------------------------------------------------------
# POST /api/payment/initiate
# ---------------------------------------------------------------------------

@payment_bp.route('/initiate', methods=['POST'])
@payment_bp.route('/create-order', methods=['POST'])
@jwt_required()
def initiate_payment():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    method = (data.get('method') or '').strip().lower()
    order_id = data.get('order_id')
    saved_method_id = data.get('saved_method_id')

    if method not in {'cod', 'upi', 'card'}:
        return _err('Invalid payment method')
    if not _rate_limit_payment_attempts(user_id):
        return _err('Too many payment attempts. Please wait a few minutes.', 429)

    order = _get_user_order(order_id, user_id)
    if not order:
        return _err('Order not found', 404)
    if order.status not in {'placed', 'pending', 'confirmed'}:
        return _err('Order cannot be paid in its current state')

    amount_paise = int(round(float(order.total_amount or 0) * 100))

    saved_method = None
    if saved_method_id:
        saved_method = SavedPaymentMethod.query.filter_by(id=saved_method_id, user_id=user_id).first()
        if not saved_method:
            return _err('Saved payment method not found', 404)
        if saved_method.type != method:
            return _err('Saved payment method type mismatch')

    try:
        # ------------------------------------------------------------------ COD
        if method == 'cod':
            payment = Payment(
                id=str(uuid.uuid4()),
                order_id=order.id,
                user_id=user_id,
                method='cod',
                razorpay_order_id=f'cod_ref_{uuid.uuid4().hex[:16]}',
                amount=amount_paise,
                currency='INR',
                status='pending',
            )
            order.payment_method = 'cod'
            order.payment_status = 'cod_pending'
            order.status = 'confirmed'
            db.session.add(payment)
            db.session.commit()
            notify_runners_new_order(order)
            return jsonify({
                'success': True,
                'method': 'cod',
                'message': 'Pay on delivery',
                'payment': payment.to_dict(),
            }), 200

        # ------------------------------------------------------------------ UPI
        if method == 'upi':
            upi_id = (saved_method.upi_id if saved_method else (data.get('upi_id') or '')).strip()
            if not UPI_REGEX.match(upi_id):
                return _err('Enter a valid UPI ID')

            # Mock Razorpay order — replace create_razorpay_order call with real one when ready
            mock_order = create_razorpay_order(amount=amount_paise, receipt=order.id)
            payment = Payment(
                id=str(uuid.uuid4()),
                order_id=order.id,
                user_id=user_id,
                method='upi',
                amount=amount_paise,
                currency='INR',
                status='pending',
                razorpay_order_id=mock_order['id'],
                upi_id=upi_id,
            )
            order.payment_method = 'upi'
            order.payment_status = 'pending'
            db.session.add(payment)
            db.session.commit()
            return jsonify({
                'success': True,
                'method': 'upi',
                'razorpay_order_id': payment.razorpay_order_id,
                'razorpay_key_id': get_razorpay_key_id(),
                'amount': payment.amount,
                'currency': payment.currency,
                'upi_id': payment.upi_id,
                # Always mock — remove this flag when real Razorpay keys are set
                'mock_checkout': True,
                'mock_payment_id': _mock_payment_id(),
                'mock_signature': 'mock_signature',
                'payment': payment.to_dict(),
            }), 200

        # ------------------------------------------------------------------ CARD
        if saved_method:
            card_last4 = saved_method.card_last4
            card_number_hash = saved_method.card_number_hash
            card_holder_name = saved_method.card_holder_name
            card_expiry = saved_method.card_expiry
        else:
            card_number = normalize_card_number(data.get('card_number') or '')
            card_holder_name = (data.get('card_holder_name') or '').strip()
            card_expiry = (data.get('card_expiry') or '').strip()
            card_pin = str(data.get('card_pin') or '').strip()

            if not is_valid_luhn(card_number):
                return _err('Enter a valid card number')
            if not card_holder_name:
                return _err('Cardholder name is required')
            if not validate_card_expiry(card_expiry):
                return _err('Card expiry is invalid or already expired')
            if not CARD_PIN_REGEX.match(card_pin):
                return _err('Card PIN must be 4 to 6 digits')

            card_last4 = card_number[-4:]
            card_number_hash = hash_card_number(card_number)
            del card_pin, card_number

        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=order.id,
            user_id=user_id,
            method='card',
            razorpay_order_id=f'card_ref_{uuid.uuid4().hex[:16]}',
            razorpay_payment_id=_mock_payment_id(),
            amount=amount_paise,
            currency='INR',
            status='success',
            card_last4=card_last4,
            card_number_hash=card_number_hash,
            card_holder_name=card_holder_name,
            card_expiry=card_expiry,
        )
        order.payment_method = 'card'
        order.payment_status = 'paid'
        order.status = 'confirmed'
        db.session.add(payment)
        db.session.commit()
        notify_runners_new_order(order)
        return jsonify({
            'success': True,
            'method': 'card',
            'card_last4': card_last4,
            'transaction_id': payment.razorpay_payment_id,
            'payment': payment.to_dict(),
        }), 200

    except Exception as exc:
        db.session.rollback()
        return _err(str(exc), 500)


# ---------------------------------------------------------------------------
# POST /api/payment/verify-upi  (mock: always succeeds)
# ---------------------------------------------------------------------------

@payment_bp.route('/verify-upi', methods=['POST'])
@payment_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_upi_payment():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id') or _mock_payment_id()
    razorpay_signature = data.get('razorpay_signature') or 'mock_signature'

    payment = Payment.query.filter_by(razorpay_order_id=razorpay_order_id, user_id=user_id).first()
    if not payment:
        return _err('Payment order not found', 404)

    order = _get_user_order(payment.order_id, user_id)
    if not order:
        return _err('Order not found', 404)

    # Mock always passes — verify_razorpay_signature returns True for any non-empty signature
    if not verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        payment.status = 'failed'
        db.session.commit()
        return _err('Payment verification failed')

    try:
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'success'
        order.payment_status = 'paid'
        order.payment_method = 'upi'
        order.status = 'confirmed'
        db.session.commit()
        notify_runners_new_order(order)
        return jsonify({
            'success': True,
            'payment_id': razorpay_payment_id,
            'payment': payment.to_dict(),
        }), 200
    except Exception as exc:
        db.session.rollback()
        return _err(str(exc), 500)


# ---------------------------------------------------------------------------
# GET /api/payment/history
# ---------------------------------------------------------------------------

@payment_bp.route('/history', methods=['GET'])
@jwt_required()
def payment_history():
    user_id = get_jwt_identity()
    payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
    return jsonify({'payments': [p.to_dict() for p in payments]}), 200


# ---------------------------------------------------------------------------
# POST /api/payment/refund/<payment_id>  (admin/staff only)
# ---------------------------------------------------------------------------

@payment_bp.route('/refund/<payment_id>', methods=['POST'])
@jwt_required()
def refund_payment(payment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role not in {'admin', 'staff'}:
        return _err('Unauthorized', 403)

    payment = Payment.query.filter(
        (Payment.id == payment_id) | (Payment.razorpay_payment_id == payment_id)
    ).first()
    if not payment:
        return _err('Payment not found', 404)

    try:
        # issue_refund is a no-op in mock mode; uncomment real Razorpay call in payment_service.py
        if payment.method in {'upi', 'card'} and payment.razorpay_payment_id:
            try:
                issue_refund(payment.razorpay_payment_id)
            except Exception:
                pass

        payment.status = 'refunded' if payment.method != 'cod' else 'cancelled'
        order = Order.query.get(payment.order_id)
        if order:
            order.payment_status = 'refunded'
        db.session.commit()
        return jsonify({'success': True, 'payment': payment.to_dict()}), 200
    except Exception as exc:
        db.session.rollback()
        return _err(str(exc), 500)
