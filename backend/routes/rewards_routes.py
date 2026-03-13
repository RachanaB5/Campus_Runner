from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, RewardPoints, RewardTransaction, Order, User
import uuid
from datetime import datetime

rewards_bp = Blueprint('rewards', __name__)

@rewards_bp.route('/my-points', methods=['GET'])
@jwt_required()
def get_my_points():
    """Get user's reward points"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get or create reward points
        reward = RewardPoints.query.filter_by(user_id=user_id).first()
        
        if not reward:
            # Create reward points if doesn't exist
            reward = RewardPoints(
                id=str(uuid.uuid4()),
                user_id=user_id,
                total_points=0,
                points_balance=0,
                tier='bronze'
            )
            db.session.add(reward)
            db.session.commit()
        
        # Calculate points based on orders
        orders = Order.query.filter_by(customer_id=user_id, status='delivered').all()
        order_count = len(orders)
        
        # 1 point per order + 5 bonus on first order
        calculated_points = order_count + (5 if order_count > 0 else 0)
        
        return jsonify({
            'points_balance': calculated_points,
            'total_points': calculated_points,
            'tier': reward.tier,
            'order_count': order_count
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rewards_bp.route('/redeem', methods=['POST'])
@jwt_required()
def redeem_points():
    """Redeem reward points"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        points_to_redeem = int(data.get('points', 0))
        
        if points_to_redeem <= 0:
            return jsonify({'error': 'Invalid points amount'}), 400
        
        # Get user's reward points
        reward = RewardPoints.query.filter_by(user_id=user_id).first()
        
        if not reward:
            return jsonify({'error': 'You have no reward points'}), 400
        
        # Calculate current balance based on orders
        orders = Order.query.filter_by(customer_id=user_id, status='delivered').all()
        order_count = len(orders)
        current_balance = order_count + (5 if order_count > 0 else 0)
        
        if current_balance < points_to_redeem:
            return jsonify({'error': 'Insufficient reward points'}), 400
        
        # Create redemption transaction
        transaction = RewardTransaction(
            id=str(uuid.uuid4()),
            reward_points_id=reward.id,
            transaction_type='redeemed',
            points=points_to_redeem,
            description=f'Redeemed {points_to_redeem} points for reward'
        )
        
        # Update reward record
        reward.total_points += points_to_redeem
        reward.points_balance = max(0, reward.points_balance - points_to_redeem)
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Reward redeemed successfully',
            'points_redeemed': points_to_redeem,
            'remaining_balance': current_balance - points_to_redeem
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rewards_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get user's reward transactions"""
    try:
        user_id = get_jwt_identity()
        reward = RewardPoints.query.filter_by(user_id=user_id).first()
        
        if not reward:
            return jsonify({'transactions': []}), 200
        
        transactions = RewardTransaction.query.filter_by(reward_points_id=reward.id).all()
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rewards_bp.route('/claim-daily-bonus', methods=['POST'])
@jwt_required()
def claim_daily_bonus():
    """Claim daily bonus points"""
    try:
        user_id = get_jwt_identity()
        reward = RewardPoints.query.filter_by(user_id=user_id).first()
        
        if not reward:
            return jsonify({'error': 'Reward account not found'}), 404
        
        # Check if already claimed today
        today = datetime.utcnow().date()
        last_bonus = RewardTransaction.query.filter_by(
            reward_points_id=reward.id,
            transaction_type='daily_bonus'
        ).order_by(RewardTransaction.created_at.desc()).first()
        
        if last_bonus and last_bonus.created_at.date() == today:
            return jsonify({'error': 'Daily bonus already claimed'}), 400
        
        # Add 5 bonus points
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
