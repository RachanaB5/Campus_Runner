from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, User, Food, Delivery, RewardPoints, RewardTransaction, Review, OrderOTP, Runner
from datetime import datetime, timedelta
import uuid

order_bp = Blueprint('order', __name__)

def generate_order_number():
    """Generate unique order number"""
    from datetime import datetime
    date = datetime.utcnow().strftime('%Y%m%d')
    random_part = str(uuid.uuid4()).split('-')[0][:4].upper()
    return f'ORD-{date}-{random_part}'

def get_available_runner():
    """Find an available runner for delivery"""
    # Get a runner who is registered and available
    runner = User.query.filter_by(role='runner').first()
    return runner


def _format_time(value):
    if not value:
        return None
    return value.strftime('%I:%M %p').lstrip('0')


def _get_reviewable_items(order, user_id):
    existing = {
        (review.order_id, review.food_id)
        for review in Review.query.filter_by(user_id=user_id).all()
    }
    items = []
    for item in order.items or []:
        if (order.id, item.food_id) not in existing:
            items.append({
                'food_id': item.food_id,
                'food_name': item.food.name if item.food else 'Item',
                'image_url': item.food.image_url if item.food else None,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'customizations': item.customizations,
            })
    return items

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
        
        # Create delivery record and auto-assign runner
        delivery = Delivery(
            id=str(uuid.uuid4()),
            order_id=order.id,
            status='pending',
            estimated_time_minutes=45
        )
        
        # Try to assign an available runner
        runner = get_available_runner()
        if runner:
            delivery.runner_id = runner.id
            delivery.status = 'assigned'
            order.status = 'confirmed'
        else:
            order.status = 'pending'
        
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
        
        response_orders = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['reviewable_items'] = _get_reviewable_items(order, user_id) if order.status == 'delivered' else []
            order_dict['has_unreviewed_items'] = order.status == 'delivered' and len(order_dict['reviewable_items']) > 0
            response_orders.append(order_dict)

        return jsonify({
            'orders': response_orders
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    """Get order details with delivery tracking"""
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Only allow user to view their own orders
        if order.customer_id != user_id and User.query.get(user_id).role not in ['admin', 'staff']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        order_dict = order.to_dict()
        
        # Add delivery tracking information
        if order.delivery:
            delivery_dict = order.delivery.to_dict()
            order_dict['delivery'] = delivery_dict
            order_dict['tracked_status'] = get_order_tracked_status(order.delivery)
        
        return jsonify(order_dict), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_order_tracked_status(delivery):
    """Get user-friendly tracked status"""
    status_mapping = {
        'pending': {
            'stage': 1,
            'title': 'Order Received',
            'description': 'Your order has been received and is being prepared',
            'icon': 'CheckCircle'
        },
        'assigned': {
            'stage': 2,
            'title': 'Delivery Partner Assigned',
            'description': f'Your delivery partner will pick up your order soon',
            'icon': 'User'
        },
        'picked_up': {
            'stage': 3,
            'title': 'Order on the Way',
            'description': 'Your order is on the way to you',
            'icon': 'Bike'
        },
        'in_transit': {
            'stage': 3,
            'title': 'Order on the Way',
            'description': 'Your order is on the way to you',
            'icon': 'Bike'
        },
        'delivered': {
            'stage': 4,
            'title': 'Order Delivered',
            'description': 'Your order has been delivered',
            'icon': 'CheckCircle'
        }
    }
    
    return status_mapping.get(delivery.status, {
        'stage': 0,
        'title': 'Processing',
        'description': 'Your order is being processed',
        'icon': 'Clock'
    })

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


@order_bp.route('/<order_id>/track', methods=['GET'])
@jwt_required()
def get_order_tracking(order_id):
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        if order.customer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        delivery = order.delivery
        delivery_otp = None
        pickup_otp = None
        if delivery:
            delivery_otp_obj = OrderOTP.query.filter_by(order_id=order.id, delivery_id=delivery.id, otp_type='delivery').order_by(OrderOTP.created_at.desc()).first()
            delivery_otp = delivery_otp_obj.otp if delivery_otp_obj else None
            pickup_otp_obj = OrderOTP.query.filter_by(order_id=order.id, delivery_id=delivery.id, otp_type='pickup').order_by(OrderOTP.created_at.desc()).first()
            pickup_otp = pickup_otp_obj.otp if pickup_otp_obj else None

        runner_info = None
        if delivery and delivery.runner_id:
            runner_user = User.query.get(delivery.runner_id)
            runner_profile = Runner.query.filter_by(user_id=delivery.runner_id).first()
            runner_info = {
                'name': runner_user.name if runner_user else None,
                'rating': round(runner_profile.average_rating, 1) if runner_profile else 4.8,
                'completed_deliveries': runner_profile.total_deliveries if runner_profile else 0,
                'phone': runner_user.phone if runner_user and order.status in ['picked_up', 'in_transit', 'on_the_way', 'delivered'] else None,
            }

        subtotal = sum(item.total_price for item in (order.items or []))
        tax = max(0.0, round(float(order.total_amount or 0) - float(order.delivery_fee or 0) - float(subtotal or 0), 2))
        timeline = [
            {'status': 'placed', 'label': 'Order Placed', 'time': _format_time(order.created_at), 'done': True},
            {'status': 'accepted', 'label': "Accepted by Mingo's", 'time': _format_time(order.received_by_canteen_at or order.created_at), 'done': order.status not in ['placed', 'pending']},
            {'status': 'runner_assigned', 'label': 'Runner Assigned', 'time': _format_time(delivery.accepted_at if delivery else None), 'done': bool(delivery and delivery.runner_id)},
            {'status': 'picked_up', 'label': 'Picked Up by Runner', 'time': _format_time(order.picked_up_at or (delivery.picked_at if delivery else None)), 'done': order.status in ['picked_up', 'in_transit', 'on_the_way', 'delivered']},
            {'status': 'on_the_way', 'label': 'Order On the Way', 'time': _format_time(order.in_transit_at or (delivery.on_the_way_at if delivery else None)), 'done': order.status in ['in_transit', 'on_the_way', 'delivered']},
            {'status': 'delivered', 'label': 'Order Delivered', 'time': _format_time(order.delivered_at), 'done': order.status == 'delivered'},
        ]

        return jsonify({
            'order_id': order.id,
            'token_number': order.order_number,
            'status': order.status,
            'payment_method': order.payment_method,
            'payment_status': order.payment_status,
            'total_amount': order.total_amount,
            'subtotal': subtotal,
            'delivery_fee': order.delivery_fee,
            'tax': tax,
            'items': [item.to_dict() for item in (order.items or [])],
            'placed_at': order.created_at.isoformat() if order.created_at else None,
            'estimated_delivery': order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None,
            'delivery_otp': delivery_otp,
            'pickup_otp': pickup_otp,
            'runner': runner_info,
            'timeline': timeline,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@order_bp.route('/<order_id>/reviewable-items', methods=['GET'])
@jwt_required()
def get_reviewable_items(order_id):
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        if order.customer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        if order.status != 'delivered':
            return jsonify({'items': []}), 200
        return jsonify({'items': _get_reviewable_items(order, user_id)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@order_bp.route('/<order_id>/receive', methods=['POST'])
@jwt_required()
def receive_order(order_id):
    """Mark order as received by canteen"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is admin or canteen staff
        if user.role not in ['admin', 'staff']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order.status = 'received'
        order.received_by_canteen_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"✅ Order {order.order_number} received by canteen")
        
        return jsonify({
            'message': 'Order received by canteen',
            'order': order.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@order_bp.route('/<order_id>/start-preparation', methods=['POST'])
@jwt_required()
def start_preparation(order_id):
    """Mark order as preparation started"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role not in ['admin', 'staff']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.status != 'received':
            return jsonify({'error': 'Order must be received first'}), 400
        
        order.status = 'preparing'
        order.preparation_started_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"✅ Order {order.order_number} preparation started")
        
        return jsonify({
            'message': 'Order preparation started',
            'order': order.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@order_bp.route('/<order_id>/mark-ready', methods=['POST'])
@jwt_required()
def mark_ready(order_id):
    """Mark order as ready for pickup"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role not in ['admin', 'staff']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.status != 'preparing':
            return jsonify({'error': 'Order must be in preparation'}), 400
        
        order.status = 'ready'
        order.ready_for_pickup_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"✅ Order {order.order_number} ready for pickup")
        
        return jsonify({
            'message': 'Order marked as ready',
            'order': order.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
