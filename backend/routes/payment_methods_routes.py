import re
import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import db, SavedPaymentMethod
from services.payment_service import hash_card_number, is_valid_luhn, normalize_card_number, validate_card_expiry

payment_methods_bp = Blueprint('payment_methods', __name__)

UPI_REGEX = re.compile(r'^[\w.\-]{3,}@[\w]{3,}$')
CARD_PIN_REGEX = re.compile(r'^\d{4,6}$')


def _detect_brand(card_number: str) -> str:
    digits = normalize_card_number(card_number)
    if digits.startswith('4'):
        return 'Visa'
    if re.match(r'^5[1-5]', digits):
        return 'Mastercard'
    if digits.startswith('6'):
        return 'RuPay'
    return 'Card'


@payment_methods_bp.route('', methods=['GET'])
@jwt_required()
def list_payment_methods():
    user_id = get_jwt_identity()
    methods = SavedPaymentMethod.query.filter_by(user_id=user_id).order_by(
        SavedPaymentMethod.is_default.desc(),
        SavedPaymentMethod.created_at.desc(),
    ).all()
    return jsonify({'payment_methods': [method.to_dict() for method in methods]}), 200


@payment_methods_bp.route('', methods=['POST'])
@jwt_required()
def add_payment_method():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    method_type = (data.get('type') or '').strip().lower()
    is_default = bool(data.get('is_default'))

    if method_type not in {'card', 'upi'}:
        return jsonify({'error': 'Invalid payment method type'}), 400

    if is_default:
        SavedPaymentMethod.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})

    if method_type == 'upi':
        upi_id = (data.get('upi_id') or '').strip()
        nickname = (data.get('upi_nickname') or '').strip()
        if not UPI_REGEX.match(upi_id):
            return jsonify({'error': 'Enter a valid UPI ID'}), 400

        method = SavedPaymentMethod(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type='upi',
            upi_id=upi_id,
            upi_nickname=nickname or 'Saved UPI',
            is_default=is_default,
        )
        db.session.add(method)
        db.session.commit()
        return jsonify({'success': True, 'payment_method': method.to_dict()}), 201

    card_number = normalize_card_number(data.get('card_number') or '')
    holder_name = (data.get('card_holder_name') or '').strip()
    expiry = (data.get('card_expiry') or '').strip()
    pin = str(data.get('card_pin') or '').strip()

    if not is_valid_luhn(card_number):
        return jsonify({'error': 'Enter a valid card number'}), 400
    if not holder_name:
        return jsonify({'error': 'Cardholder name is required'}), 400
    if not validate_card_expiry(expiry):
        return jsonify({'error': 'Card expiry is invalid or expired'}), 400
    if not CARD_PIN_REGEX.match(pin):
        return jsonify({'error': 'PIN must be 4 to 6 digits'}), 400

    method = SavedPaymentMethod(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type='card',
        card_last4=card_number[-4:],
        card_holder_name=holder_name,
        card_expiry=expiry,
        card_brand=_detect_brand(card_number),
        card_number_hash=hash_card_number(card_number),
        is_default=is_default,
    )
    db.session.add(method)
    db.session.commit()
    return jsonify({'success': True, 'payment_method': method.to_dict()}), 201


@payment_methods_bp.route('/<method_id>', methods=['DELETE'])
@jwt_required()
def delete_payment_method(method_id):
    user_id = get_jwt_identity()
    method = SavedPaymentMethod.query.filter_by(id=method_id, user_id=user_id).first()
    if not method:
        return jsonify({'error': 'Payment method not found'}), 404
    db.session.delete(method)
    db.session.commit()
    return jsonify({'success': True}), 200


@payment_methods_bp.route('/<method_id>/default', methods=['PUT'])
@jwt_required()
def set_default_payment_method(method_id):
    user_id = get_jwt_identity()
    method = SavedPaymentMethod.query.filter_by(id=method_id, user_id=user_id).first()
    if not method:
        return jsonify({'error': 'Payment method not found'}), 404
    SavedPaymentMethod.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    method.is_default = True
    db.session.commit()
    return jsonify({'success': True, 'payment_method': method.to_dict()}), 200
