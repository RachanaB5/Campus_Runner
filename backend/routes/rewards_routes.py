from datetime import datetime
import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.models import Order, RewardPoints, RewardTransaction, User, db

rewards_bp = Blueprint('rewards', __name__)

DEFAULT_VOUCHERS = [
    {
        'id': 'free-delivery',
        'name': 'Hostel Hopper Pass',
        'description': 'Skip the delivery fee on your next late-night campus order.',
        'points_required': 100,
        'discount_type': 'delivery',
        'discount_value': 10,
        'is_active': True,
        'category': 'Delivery',
        'image': 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop',
    },
    {
        'id': 'ten-off',
        'name': 'Snack Sprint Saver',
        'description': 'Save ₹10 on a quick bite when you need a fast campus refuel.',
        'points_required': 150,
        'discount_type': 'flat',
        'discount_value': 10,
        'is_active': True,
        'category': 'Discount',
        'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop',
    },
    {
        'id': 'twenty-five-off',
        'name': 'Feast Mode Voucher',
        'description': 'Knock ₹25 off a bigger order for your next proper meal break.',
        'points_required': 300,
        'discount_type': 'flat',
        'discount_value': 25,
        'is_active': True,
        'category': 'Discount',
        'image': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop',
    },
]

BONUS_VOUCHER_ROTATION = [
    {
        'id': 'bonus-maggi',
        'name': 'Midnight Maggi Pass',
        'description': 'Unlock a ₹20 instant discount for those late-study hunger pangs.',
        'points_required': 220,
        'discount_type': 'flat',
        'discount_value': 20,
        'is_active': True,
        'category': 'Night Owl',
        'image': 'https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=400&h=300&fit=crop',
    },
    {
        'id': 'bonus-brew',
        'name': 'Caffeine Rescue Coupon',
        'description': 'Save ₹15 on your next coffee, shake, or beverage run.',
        'points_required': 180,
        'discount_type': 'flat',
        'discount_value': 15,
        'is_active': True,
        'category': 'Beverage',
        'image': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=300&fit=crop',
    },
    {
        'id': 'bonus-combo',
        'name': 'Combo Craving Deal',
        'description': 'Take ₹30 off when you are ready to order a bigger combo meal.',
        'points_required': 360,
        'discount_type': 'flat',
        'discount_value': 30,
        'is_active': True,
        'category': 'Combo',
        'image': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=300&fit=crop',
    },
]


def _get_or_create_reward_account(user_id: str) -> RewardPoints:
    reward = RewardPoints.query.filter_by(user_id=user_id).first()
    if reward:
        return reward

    reward = RewardPoints(
        id=str(uuid.uuid4()),
        user_id=user_id,
        total_points=0,
        points_balance=0,
        tier='bronze',
    )
    db.session.add(reward)
    db.session.commit()
    return reward


def _voucher_by_id(voucher_id: str):
    catalog = DEFAULT_VOUCHERS + BONUS_VOUCHER_ROTATION
    return next((voucher for voucher in catalog if voucher['id'] == voucher_id and voucher.get('is_active')), None)


def _build_voucher_code(voucher_id: str) -> str:
    return f"CR-{voucher_id[:4].upper()}-{uuid.uuid4().hex[:6].upper()}"


def _serialize_voucher_transaction(transaction: RewardTransaction):
    description = transaction.description or ''
    if not description.startswith('VOUCHER|'):
        return None

    parts = description.split('|')
    if len(parts) < 8:
        return None

    _, voucher_id, name, discount_type, discount_value, code, status, redeemed_at = parts[:8]
    return {
        'transaction_id': transaction.id,
        'voucher_id': voucher_id,
        'name': name,
        'discount_type': discount_type,
        'discount_value': float(discount_value),
        'code': code,
        'status': status,
        'is_used': status == 'used',
        'redeemed_at': redeemed_at,
        'points_required': transaction.points,
        'category': 'Discount' if discount_type == 'flat' else 'Delivery',
        'description': name,
        'image': None,
    }


def _build_available_vouchers(reward: RewardPoints | None):
    base_vouchers = [dict(voucher) for voucher in DEFAULT_VOUCHERS]
    if not reward:
        return base_vouchers

    transactions = RewardTransaction.query.filter_by(
        reward_points_id=reward.id,
        transaction_type='redeemed',
    ).all()
    used_count = 0
    redeemed_bonus_ids = set()
    for transaction in transactions:
        voucher = _serialize_voucher_transaction(transaction)
        if not voucher:
            continue
        if voucher['is_used']:
            used_count += 1
        if str(voucher['voucher_id']).startswith('bonus-'):
            redeemed_bonus_ids.add(voucher['voucher_id'])

    bonus_index = min(used_count, len(BONUS_VOUCHER_ROTATION) - 1) if BONUS_VOUCHER_ROTATION else 0
    if BONUS_VOUCHER_ROTATION:
        candidate_bonus = dict(BONUS_VOUCHER_ROTATION[bonus_index])
        if candidate_bonus['id'] not in redeemed_bonus_ids:
            base_vouchers.append(candidate_bonus)

    return base_vouchers


@rewards_bp.route('/my-points', methods=['GET'])
@jwt_required()
def get_my_points():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        reward = _get_or_create_reward_account(user_id)
        order_count = Order.query.filter_by(customer_id=user_id, status='delivered').count()
        voucher_transactions = RewardTransaction.query.filter_by(
            reward_points_id=reward.id,
            transaction_type='redeemed',
        ).order_by(RewardTransaction.created_at.desc()).all()
        available_vouchers = [
            voucher for voucher in (_serialize_voucher_transaction(tx) for tx in voucher_transactions)
            if voucher and not voucher['is_used']
        ]

        return jsonify({
            'points_balance': reward.points_balance,
            'total_points': reward.total_points,
            'tier': reward.tier,
            'order_count': order_count,
            'available_vouchers': available_vouchers,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/redeem', methods=['POST'])
@jwt_required()
def redeem_points():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        reward = RewardPoints.query.filter_by(user_id=user_id).first()
        if not reward:
            return jsonify({'error': 'You have no reward points'}), 400

        data = request.get_json() or {}
        voucher_id = data.get('voucher_id')
        voucher = _voucher_by_id(voucher_id) if voucher_id else None
        points_to_redeem = int(voucher['points_required']) if voucher else int(data.get('points', 0))

        if points_to_redeem <= 0:
            return jsonify({'error': 'Invalid points amount'}), 400
        if reward.points_balance < points_to_redeem:
            return jsonify({'error': 'Insufficient reward points'}), 400

        voucher_code = None
        description = f'Redeemed {points_to_redeem} points for reward'
        if voucher:
            voucher_code = _build_voucher_code(voucher['id'])
            description = (
                f"VOUCHER|{voucher['id']}|{voucher['name']}|{voucher['discount_type']}|"
                f"{voucher['discount_value']}|{voucher_code}|unused|{datetime.utcnow().isoformat()}"
            )

        transaction = RewardTransaction(
            id=str(uuid.uuid4()),
            reward_points_id=reward.id,
            transaction_type='redeemed',
            points=points_to_redeem,
            description=description,
        )

        reward.points_balance = max(0, reward.points_balance - points_to_redeem)
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'message': 'Reward redeemed successfully',
            'voucher': _serialize_voucher_transaction(transaction),
            'points_redeemed': points_to_redeem,
            'remaining_balance': reward.points_balance,
            'voucher_code': voucher_code,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/available', methods=['GET'])
@rewards_bp.route('/vouchers', methods=['GET'])
@jwt_required()
def get_available_rewards():
    user_id = get_jwt_identity()
    reward = RewardPoints.query.filter_by(user_id=user_id).first()
    balance = reward.points_balance if reward else 0
    vouchers = [{**voucher, 'can_redeem': balance >= voucher['points_required']} for voucher in _build_available_vouchers(reward)]
    return jsonify({'rewards': vouchers, 'vouchers': vouchers}), 200


@rewards_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_rewards_balance():
    return get_my_points()


@rewards_bp.route('/history', methods=['GET'])
@jwt_required()
def get_rewards_history():
    return get_transactions()


@rewards_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        user_id = get_jwt_identity()
        reward = RewardPoints.query.filter_by(user_id=user_id).first()
        if not reward:
            return jsonify({'transactions': [], 'vouchers': []}), 200

        transactions = RewardTransaction.query.filter_by(reward_points_id=reward.id).order_by(
            RewardTransaction.created_at.desc()
        ).all()
        vouchers = [voucher for voucher in (_serialize_voucher_transaction(tx) for tx in transactions) if voucher]

        return jsonify({
            'transactions': [t.to_dict() for t in transactions],
            'vouchers': vouchers,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/claim-daily-bonus', methods=['POST'])
@jwt_required()
def claim_daily_bonus():
    try:
        user_id = get_jwt_identity()
        reward = RewardPoints.query.filter_by(user_id=user_id).first()
        if not reward:
            return jsonify({'error': 'Reward account not found'}), 404

        today = datetime.utcnow().date()
        last_bonus = RewardTransaction.query.filter_by(
            reward_points_id=reward.id,
            transaction_type='daily_bonus'
        ).order_by(RewardTransaction.created_at.desc()).first()

        if last_bonus and last_bonus.created_at.date() == today:
            return jsonify({'error': 'Daily bonus already claimed'}), 400

        bonus_points = 5
        transaction = RewardTransaction(
            id=str(uuid.uuid4()),
            reward_points_id=reward.id,
            transaction_type='daily_bonus',
            points=bonus_points,
            description='Daily login bonus'
        )

        reward.total_points += bonus_points
        reward.points_balance += bonus_points
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'message': 'Daily bonus claimed',
            'points_earned': bonus_points
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/redeemed-vouchers', methods=['GET'])
@jwt_required()
def get_redeemed_vouchers():
    user_id = get_jwt_identity()
    reward = RewardPoints.query.filter_by(user_id=user_id).first()
    if not reward:
        return jsonify({'vouchers': []}), 200

    transactions = RewardTransaction.query.filter_by(
        reward_points_id=reward.id,
        transaction_type='redeemed',
    ).order_by(RewardTransaction.created_at.desc()).all()
    vouchers = [voucher for voucher in (_serialize_voucher_transaction(tx) for tx in transactions) if voucher]
    return jsonify({'vouchers': vouchers}), 200
