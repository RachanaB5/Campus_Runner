from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, User, Food, Delivery, RewardPoints, RewardTransaction
from datetime import datetime, timedelta
import uuid

order_bp = Blueprint('order', __name__)

def generate_order_number():
    """Generate unique order number"""
    from datetime import datetime
    date = datetime.utcnow().strftime('%Y%m%d')
    random_part = str(uuid.uuid4()).split('-')[0][:4].upper()
    return f'ORD-{date}-{random_part}'

@order_bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'Order must contain items'}), 400
        
        # Calculate total amount
        total_amount = 0
        order_items = []
        
        for item in items:
            food = Food.query.get(item['food_id'])
            if not food:
                return jsonify({'error': f'Food {item["food_id"]} not found'}), 404
            
            quantity = int(item['quantity'])
            unit_price = float(item.get('price', food.price))
            total_price = unit_price * quantity
            total_amount += total_price
            
            order_item = OrderItem(
                id=str(uuid.uuid4()),
                food_id=food.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            order_items.append(order_item)
        
        # Get the total from frontend (includes taxes and delivery)
        final_total = float(data.get('total_price', total_amount))
        delivery_fee = float(data.get('delivery_fee', 0))
        
        # Create order
        order = Order(
            id=str(uuid.uuid4()),
            customer_id=user_id,
            order_number=generate_order_number(),
            total_amount=final_total,
            delivery_fee=delivery_fee,
            delivery_address=data.get('delivery_location'),
            customer_phone=data.get('customer_phone'),
            special_instructions=data.get('delivery_instructions'),
            status='pending',
            payment_method=data.get('payment_method', 'cash')
        )
        
        for order_item in order_items:
            order.items.append(order_item)
        
        # Create delivery record
        delivery = Delivery(
            id=str(uuid.uuid4()),
            order_id=order.id,
            status='pending',
            estimated_time=datetime.utcnow() + timedelta(minutes=45)
        )
        db.session.add(delivery)
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@order_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """Get user's orders"""
    try:
        user_id = get_jwt_identity()
        orders = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc()).all()
        
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    """Get order details"""
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify(order.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.customer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if order.status not in ['pending', 'confirmed']:
            return jsonify({'error': 'Order cannot be cancelled'}), 400
        
        order.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<order_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_order(order_id):
    """Confirm order payment"""
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.customer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        order.status = 'confirmed'
        order.payment_status = 'completed'
        
        # Calculate and add reward points
        reward_points = int(order.total_amount / 10)  # 1 point per ₹10
        
        user_reward = RewardPoints.query.filter_by(user_id=user_id).first()
        if user_reward:
            user_reward.total_points += reward_points
            user_reward.points_balance += reward_points
            
            # Create transaction record
            transaction = RewardTransaction(
                id=str(uuid.uuid4()),
                reward_points_id=user_reward.id,
                order_id=order.id,
                transaction_type='earned',
                points=reward_points,
                description=f'Earned from order {order.order_number}'
            )
            db.session.add(transaction)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order confirmed',
            'order': order.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (admin/staff only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'staff']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        data = request.get_json()
        if 'status' in data:
            order.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated',
            'order': order.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
