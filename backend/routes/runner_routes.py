from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Runner, Delivery, Order, OrderOTP, RewardPoints, RewardTransaction
from datetime import datetime
import uuid
from sqlalchemy import select

from services.notification_service import notify_order_taken

runner_bp = Blueprint('runner', __name__)

RUNNER_VISIBLE_ORDER_STATUSES = ['pending', 'placed', 'received', 'confirmed', 'preparing', 'ready']


def _calculate_runner_reward_points(total_amount) -> int:
    return max(10, int(round(float(total_amount or 0) * 0.1)))


def _format_customer_name(name: str | None) -> str:
    if not name:
        return 'Campus User'
    parts = name.split()
    if len(parts) == 1:
        return parts[0]
    return f'{parts[0]} {parts[-1][0]}.'


def _build_delivery_address(full_address: str | None) -> dict:
    parts = [part.strip() for part in (full_address or '').split(',') if part.strip()]
    return {
        'hostel': parts[0] if len(parts) > 0 else '',
        'room': parts[1] if len(parts) > 1 else '',
        'landmark': parts[2] if len(parts) > 2 else '',
        'full_address': full_address or '',
    }


def _emit_order_status(order, new_status, runner_name=None):
    try:
        import app as app_module

        if getattr(app_module, 'socketio', None):
            app_module.socketio.emit('order_status_update', {
                'order_id': order.id,
                'status': new_status,
                'updated_at': datetime.utcnow().isoformat(),
                'runner_name': runner_name,
            }, room=f'user:{order.customer_id}')
    except Exception:
        return


def _reward_runner(user_id: str, order, points: int):
    reward = RewardPoints.query.filter_by(user_id=user_id).first()
    if not reward:
        reward = RewardPoints(
            id=str(uuid.uuid4()),
            user_id=user_id,
            total_points=0,
            points_balance=0,
        )
        db.session.add(reward)
        db.session.flush()

    reward.total_points += points
    reward.points_balance += points
    transaction = RewardTransaction(
        id=str(uuid.uuid4()),
        reward_points_id=reward.id,
        order_id=order.id,
        transaction_type='earned',
        points=points,
        description=f'Runner reward for delivering {order.order_number}',
    )
    db.session.add(transaction)


def _runner_has_active_delivery(user_id: str) -> bool:
    return Delivery.query.filter(
        Delivery.runner_id == user_id,
        Delivery.status.in_(['assigned', 'picked_up', 'on_the_way', 'in_transit'])
    ).first() is not None

@runner_bp.route('/register', methods=['POST'])
@jwt_required()
def register_as_runner():
    """Register user as a runner"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already a runner
        if Runner.query.filter_by(user_id=user_id).first():
            return jsonify({'error': 'User is already a runner'}), 400
        
        data = request.get_json()
        
        runner = Runner(
            id=str(uuid.uuid4()),
            user_id=user_id,
            vehicle_type=data.get('vehicle_type'),
            license_number=data.get('license_number'),
            is_available=False,
            status='offline'
        )
        
        user.role = 'runner'
        db.session.add(runner)
        db.session.commit()
        
        return jsonify({
            'message': 'Registered as runner',
            'runner': runner.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@runner_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_runner_profile():
    """Get runner profile"""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404
        
        return jsonify(runner.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@runner_bp.route('/update-location', methods=['POST'])
@jwt_required()
def update_location():
    """Update runner's current location"""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404
        
        data = request.get_json()
        runner.current_latitude = data.get('latitude')
        runner.current_longitude = data.get('longitude')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Location updated',
            'runner': runner.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@runner_bp.route('/toggle-availability', methods=['POST'])
@jwt_required()
def toggle_availability():
    """Toggle runner availability"""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404
        
        runner.is_available = not runner.is_available
        runner.status = 'online' if runner.is_available else 'offline'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Availability updated',
            'runner': runner.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/status', methods=['GET'])
@jwt_required()
def get_runner_status():
    """Single source of truth for runner availability and active delivery state."""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()

        if not runner:
            return jsonify({
                'is_runner': False,
                'is_available': False,
                'has_active_delivery': False,
                'active_delivery_id': None,
                'completed_deliveries': 0,
                'total_earnings': 0,
                'status': 'offline',
            }), 200

        active_delivery = Delivery.query.filter(
            Delivery.runner_id == user_id,
            Delivery.status.in_(['assigned', 'picked_up', 'on_the_way', 'in_transit'])
        ).order_by(Delivery.created_at.desc()).first()

        return jsonify({
            'is_runner': True,
            'runner_id': runner.id,
            'is_available': bool(runner.is_available),
            'has_active_delivery': active_delivery is not None,
            'active_delivery_id': active_delivery.id if active_delivery else None,
            'completed_deliveries': runner.total_deliveries or 0,
            'total_earnings': runner.total_earnings or 0,
            'status': runner.status or ('online' if runner.is_available else 'offline'),
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/toggle', methods=['PUT'])
@jwt_required()
def set_runner_availability():
    """Explicit runner availability setter for shared frontend state."""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()

        if not runner:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            runner = Runner(
                id=str(uuid.uuid4()),
                user_id=user_id,
                vehicle_type='bike',
                license_number=f'AUTO-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
                is_available=False,
                status='offline',
            )
            user.role = 'runner'
            db.session.add(runner)
            db.session.flush()

        data = request.get_json(force=True, silent=True) or {}
        target = data.get('is_available')
        if target is None:
            runner.is_available = not bool(runner.is_available)
        else:
            runner.is_available = bool(target)

        if runner.status != 'on_delivery':
            runner.status = 'online' if runner.is_available else 'offline'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Runner availability updated',
            'is_available': runner.is_available,
            'runner': runner.to_dict(),
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@runner_bp.route('/available-deliveries', methods=['GET'])
@jwt_required()
def get_available_deliveries():
    """Get available deliveries for runner"""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404
        
        # Get orders with pending delivery assignment
        deliveries = Delivery.query.filter_by(status='pending').filter(
            Delivery.runner_id == None
        ).all()
        
        return jsonify({
            'deliveries': [delivery.to_dict() for delivery in deliveries]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@runner_bp.route('/accept-delivery/<delivery_id>', methods=['POST'])
@jwt_required()
def accept_delivery(delivery_id):
    """Accept a delivery"""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404
        if not runner.is_available:
            return jsonify({'error': 'Enable Runner Mode before accepting deliveries'}), 400
        if _runner_has_active_delivery(user_id):
            return jsonify({'error': 'Complete your active delivery before accepting a new one'}), 409
        
        delivery = db.session.execute(
            select(Delivery)
            .where(Delivery.id == delivery_id, Delivery.status == 'pending', Delivery.runner_id.is_(None))
            .with_for_update(skip_locked=True)
        ).scalar_one_or_none()
        
        if not delivery:
            return jsonify({'error': 'Delivery already assigned or unavailable'}), 409
        
        delivery.runner_id = user_id
        delivery.status = 'assigned'
        delivery.accepted_at = datetime.utcnow()
        runner.status = 'on_delivery'
        
        # Update order status
        order = Order.query.get(delivery.order_id)
        if order:
            order.status = 'preparing'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery accepted',
            'delivery': delivery.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@runner_bp.route('/my-deliveries', methods=['GET'])
@jwt_required()
def get_my_deliveries():
    """Get runner's deliveries"""
    try:
        user_id = get_jwt_identity()
        deliveries = Delivery.query.filter_by(runner_id=user_id).order_by(Delivery.created_at.desc()).all()
        
        return jsonify({
            'deliveries': [delivery.to_dict() for delivery in deliveries]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@runner_bp.route('/delivery/<delivery_id>/update-status', methods=['POST'])
@jwt_required()
def update_delivery_status(delivery_id):
    """Update delivery status"""
    try:
        user_id = get_jwt_identity()
        delivery = Delivery.query.get(delivery_id)
        
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        
        if delivery.runner_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        delivery.status = data.get('status')
        
        if delivery.status == 'delivered':
            delivery.actual_delivery_time = datetime.utcnow()
            runner = Runner.query.filter_by(user_id=user_id).first()
            if runner:
                runner.total_deliveries += 1
                runner.status = 'online'
            
            order = Order.query.get(delivery.order_id)
            if order:
                order.status = 'delivered'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery status updated',
            'delivery': delivery.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@runner_bp.route('/delivery/<delivery_id>/rate', methods=['POST'])
@jwt_required()
def rate_delivery(delivery_id):
    """Rate a delivery"""
    try:
        user_id = get_jwt_identity()
        delivery = Delivery.query.get(delivery_id)
        
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        
        order = Order.query.get(delivery.order_id)
        if order.customer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        delivery.rating = data.get('rating')
        delivery.review = data.get('review')
        
        # Update runner rating
        if delivery.runner_id:
            runner = Runner.query.filter_by(user_id=delivery.runner_id).first()
            if runner:
                # Calculate average rating
                runner_deliveries = Delivery.query.filter_by(runner_id=delivery.runner_id).all()
                ratings = [d.rating for d in runner_deliveries if d.rating]
                runner.average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery rated',
            'delivery': delivery.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/available-orders', methods=['GET'])
@jwt_required()
def get_available_orders():
    """Get new orders available for acceptance by online runners."""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404
        if not runner.is_available:
            return jsonify({
                'orders': [],
                'available_orders': [],
                'count': 0,
                'message': 'Enable Runner Mode to receive available orders',
            }), 200
        
        candidate_orders = Order.query.filter(
            Order.status.in_(RUNNER_VISIBLE_ORDER_STATUSES)
        ).order_by(Order.created_at.asc()).all()
        self_excluded_orders = 0

        visible_orders = [
            order for order in candidate_orders
            if order.customer_id != user_id
        ]
        self_excluded_orders = len(candidate_orders) - len(visible_orders)
        candidate_orders = visible_orders

        orders_data = []
        for order in candidate_orders:
            delivery = order.delivery
            if not delivery or not delivery.runner_id:
                customer = User.query.get(order.customer_id)
                if customer and customer.name:
                    name_parts = customer.name.strip().split()
                    customer_display = name_parts[0] + (f" {name_parts[-1][0]}." if len(name_parts) > 1 else "")
                else:
                    customer_display = 'Unknown'
                items = []
                for item in order.items or []:
                    food = item.food
                    items.append({
                        'food_id': item.food_id,
                        'name': food.name if food else 'Unknown Item',
                        'quantity': item.quantity,
                        'unit_price': float(item.unit_price or 0),
                        'subtotal': float(item.total_price or (item.quantity * item.unit_price)),
                        'is_veg': food.is_veg if food else True,
                        'image_url': food.image_url if food else None,
                        'customizations': item.customizations or '',
                    })
                first_food = order.items[0].food if order.items else None
                counter_number = getattr(first_food, 'counter_number', None) if first_food else None
                reward_points = _calculate_runner_reward_points(order.total_amount)
                orders_data.append({
                    'id': order.id,
                    'order_id': order.id,
                    'token_number': order.order_number,
                    'customer_name': customer_display,
                    'placed_at': order.created_at.isoformat() if order.created_at else None,
                    'item_count': len(items),
                    'items': items,
                    'items_preview': [entry['name'] for entry in items[:2]],
                    'items_summary': [entry['name'] for entry in items[:3]],
                    'subtotal': float(sum(entry['subtotal'] for entry in items)),
                    'delivery_fee': float(order.delivery_fee or 0),
                    'tax': max(0.0, round(float(order.total_amount or 0) - float(order.delivery_fee or 0) - float(sum(entry['subtotal'] for entry in items)), 2)),
                    'total_amount': float(order.total_amount or 0),
                    'payment_method': order.payment_method or 'N/A',
                    'payment_status': order.payment_status or 'pending',
                    'delivery_address': order.delivery_address or 'On-campus pickup',
                    'special_instructions': order.special_instructions or '',
                    'counter_number': counter_number,
                    'pickup_location': f'Counter {counter_number}' if counter_number else 'Campus kitchen',
                    'reward_points': reward_points,
                    'status': order.status,
                })

        return jsonify({
            'orders': orders_data,
            'available_orders': orders_data,
            'count': len(orders_data),
            'self_excluded_orders': self_excluded_orders,
            'message': (
                'No other users have open orders right now.'
                if len(orders_data) == 0 and self_excluded_orders == 0
                else 'Your own open orders are hidden here. Switch to a different customer account to test runner acceptance.'
                if len(orders_data) == 0 and self_excluded_orders > 0
                else None
            ),
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/accept/<order_id>', methods=['POST'])
@jwt_required()
def accept_order(order_id):
    """Assign an order to the current runner using row locking."""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()

        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404
        if not runner.is_available:
            return jsonify({'error': 'Enable Runner Mode before accepting orders'}), 400
        if _runner_has_active_delivery(user_id):
            return jsonify({'error': 'Complete your active delivery before accepting a new one'}), 409

        delivery = Delivery.query.filter_by(order_id=order_id).first()
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404

        locked_order = db.session.execute(
            select(Order)
            .where(Order.id == order_id, Order.status.in_(RUNNER_VISIBLE_ORDER_STATUSES))
            .with_for_update(skip_locked=True)
        ).scalar_one_or_none()

        if not locked_order:
            return jsonify({'error': 'Order already accepted by another runner'}), 409
        if locked_order.customer_id == user_id:
            return jsonify({'error': 'You cannot accept delivery for your own order'}), 403

        current_delivery = Delivery.query.filter_by(order_id=order_id).first()
        if current_delivery and current_delivery.runner_id:
            return jsonify({'error': 'Order already accepted by another runner'}), 409

        current_delivery.runner_id = user_id
        current_delivery.status = 'assigned'
        current_delivery.accepted_at = datetime.utcnow()
        runner.status = 'on_delivery'
        locked_order.status = 'ready' if locked_order.status == 'ready' else 'confirmed'
        db.session.commit()

        notify_order_taken(locked_order, runner_user=User.query.get(user_id))
        pickup_otp = OrderOTP.query.filter_by(order_id=locked_order.id, delivery_id=current_delivery.id, otp_type='pickup').order_by(OrderOTP.created_at.desc()).first()

        return jsonify({
            'success': True,
            'message': 'Order accepted successfully',
            'order': locked_order.to_dict(),
            'delivery_id': current_delivery.id,
            'pickup_otp': pickup_otp.otp if pickup_otp else None,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/order/<order_id>/details', methods=['GET'])
@jwt_required()
def get_runner_order_details(order_id):
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        delivery = Delivery.query.filter_by(order_id=order.id).first()
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        if delivery.runner_id and delivery.runner_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        subtotal = sum(item.total_price for item in (order.items or []))
        tax = max(0.0, round(float(order.total_amount or 0) - float(order.delivery_fee or 0) - float(subtotal or 0), 2))
        first_food = order.items[0].food if order.items else None
        counter_number = getattr(first_food, 'counter_number', None) or 1
        counter_name = getattr(first_food, 'counter_name', None) or 'Main Counter'
        pickup_otp = OrderOTP.query.filter_by(order_id=order.id, delivery_id=delivery.id, otp_type='pickup').order_by(OrderOTP.created_at.desc()).first()
        delivery_otp = OrderOTP.query.filter_by(order_id=order.id, delivery_id=delivery.id, otp_type='delivery').order_by(OrderOTP.created_at.desc()).first()
        customer = User.query.get(order.customer_id)

        return jsonify({
            'order_id': order.id,
            'delivery_id': delivery.id,
            'token_number': order.order_number,
            'placed_at': order.created_at.isoformat() if order.created_at else None,
            'estimated_prep_time': delivery.estimated_time_minutes or 18,
            'payment_method': order.payment_method,
            'payment_status': order.payment_status,
            'total_amount': order.total_amount,
            'subtotal': subtotal,
            'delivery_fee': order.delivery_fee,
            'tax': tax,
            'special_instructions': order.special_instructions,
            'delivery_address': _build_delivery_address(order.delivery_address),
            'counter_number': counter_number,
            'counter_name': counter_name,
            'items': [{
                'food_id': item.food_id,
                'name': item.food.name if item.food else 'Item',
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'subtotal': item.total_price,
                'is_veg': item.food.is_veg if item.food else True,
                'image_url': item.food.image_url if item.food else None,
                'customizations': item.customizations,
            } for item in (order.items or [])],
            'runner_reward_points': _calculate_runner_reward_points(order.total_amount),
            'customer_name': _format_customer_name(customer.name if customer else None),
            'customer_initial': (customer.name[:1].upper() if customer and customer.name else 'C'),
            'customer_phone': customer.phone if customer and delivery.status in ['picked_up', 'on_the_way', 'delivered'] else None,
            'pickup_otp': pickup_otp.otp if pickup_otp else None,
            'delivery_otp': delivery_otp.otp if delivery_otp else None,
            'delivery_status': delivery.status,
            'runner_stats': {
                'deliveries_made': runner.total_deliveries or 0,
            },
            'timeline': {
                'accepted_at': delivery.accepted_at.isoformat() if delivery.accepted_at else None,
                'picked_at': delivery.picked_at.isoformat() if delivery.picked_at else None,
                'on_the_way_at': delivery.on_the_way_at.isoformat() if delivery.on_the_way_at else None,
                'delivered_at': delivery.delivered_at.isoformat() if delivery.delivered_at else None,
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/delivery/<delivery_id>/details', methods=['GET'])
@jwt_required()
def get_runner_delivery_details(delivery_id):
    try:
        user_id = get_jwt_identity()
        delivery = Delivery.query.get(delivery_id)
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        if delivery.runner_id and delivery.runner_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        return get_runner_order_details(delivery.order_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/active-delivery', methods=['GET'])
@jwt_required()
def get_active_delivery():
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        if not runner:
            return jsonify({'active': False}), 200

        delivery = Delivery.query.filter(
            Delivery.runner_id == user_id,
            Delivery.status.in_(['assigned', 'picked_up', 'on_the_way'])
        ).order_by(Delivery.created_at.desc()).first()

        if not delivery:
            return jsonify({'active': False}), 200

        order = Order.query.get(delivery.order_id)
        if not order:
            return jsonify({'active': False}), 200

        details_response = get_runner_order_details(order.id)
        if isinstance(details_response, tuple):
            payload, status = details_response
            if status != 200:
                return jsonify({'active': False}), 200
            details = payload.get_json()
        else:
            details = details_response.get_json()

        return jsonify({
            'active': True,
            'delivery_id': delivery.id,
            'delivery_status': delivery.status,
            'details': details,
            'order': {
                'id': order.id,
                'token_number': order.order_number,
                'total_amount': float(order.total_amount or 0),
                'payment_method': order.payment_method,
                'payment_status': order.payment_status,
                'special_instructions': order.special_instructions or '',
                'delivery_address': order.delivery_address,
                'items': details.get('items', []),
                'item_count': len(details.get('items', [])),
            },
            'customer_name': details.get('customer_name'),
            'customer_phone': details.get('customer_phone'),
            'pickup_otp': details.get('pickup_otp'),
            'reward_points': details.get('runner_reward_points'),
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/delivery/<delivery_id>/status', methods=['PUT'])
@jwt_required()
def update_delivery_status_v2(delivery_id):
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404

        delivery = Delivery.query.get(delivery_id)
        if not delivery or delivery.runner_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        order = Order.query.get(delivery.order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        data = request.get_json() or {}
        new_status = data.get('status')
        otp_code = str(data.get('otp') or '').strip()
        runner_user = User.query.get(user_id)
        runner_name = runner_user.name if runner_user else None

        if new_status == 'picked_up':
            pickup_otp = OrderOTP.query.filter_by(order_id=order.id, delivery_id=delivery.id, otp_type='pickup').order_by(OrderOTP.created_at.desc()).first()
            if pickup_otp and not pickup_otp.is_verified:
                pickup_otp.is_verified = True
                pickup_otp.verified_at = datetime.utcnow()
            delivery.status = 'picked_up'
            delivery.picked_at = datetime.utcnow()
            order.status = 'picked_up'
            order.picked_up_at = datetime.utcnow()
            _emit_order_status(order, 'picked_up', runner_name)
        elif new_status == 'assigned':
            delivery.status = 'assigned'
            order.status = 'confirmed'
        elif new_status == 'on_the_way':
            delivery.status = 'on_the_way'
            delivery.on_the_way_at = datetime.utcnow()
            order.status = 'on_the_way'
            order.in_transit_at = datetime.utcnow()
            _emit_order_status(order, 'on_the_way', runner_name)
        elif new_status == 'delivered':
            delivery_otp = OrderOTP.query.filter_by(order_id=order.id, delivery_id=delivery.id, otp_type='delivery').order_by(OrderOTP.created_at.desc()).first()
            if not delivery_otp or delivery_otp.otp != otp_code:
                return jsonify({'error': 'Invalid delivery OTP'}), 400
            delivery_otp.is_verified = True
            delivery_otp.verified_at = datetime.utcnow()
            delivery.status = 'delivered'
            delivery.delivered_at = datetime.utcnow()
            delivery.actual_delivery_time = datetime.utcnow()
            order.status = 'delivered'
            order.delivered_at = datetime.utcnow()
            runner.total_deliveries = (runner.total_deliveries or 0) + 1
            runner.status = 'online'
            reward_points = _calculate_runner_reward_points(order.total_amount)
            _reward_runner(user_id, order, reward_points)
            _emit_order_status(order, 'delivered', runner_name)
        else:
            return jsonify({'error': 'Invalid status'}), 400

        db.session.commit()
        return jsonify({
            'message': 'Delivery status updated',
            'delivery': delivery.to_dict(),
            'order': order.to_dict(),
            'points_earned': _calculate_runner_reward_points(order.total_amount) if new_status == 'delivered' else 0,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/pickup-order/<order_id>', methods=['POST'])
@jwt_required()
def pickup_order(order_id):
    """Runner picks up an order"""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.status != 'ready':
            return jsonify({'error': 'Order is not ready for pickup'}), 400
        
        # Create or update delivery
        delivery = Delivery.query.filter_by(order_id=order_id).first()
        if not delivery:
            delivery = Delivery(
                id=str(uuid.uuid4()),
                order_id=order_id,
                status='picked_up'
            )
            db.session.add(delivery)
        else:
            delivery.status = 'picked_up'
        
        delivery.runner_id = user_id
        delivery.pickup_location = 'Canteen'
        delivery.delivery_location = order.delivery_address
        
        # Update order status
        order.status = 'picked_up'
        order.picked_up_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"✅ Order {order.order_number} picked up by runner")
        
        return jsonify({
            'message': 'Order picked up successfully',
            'order': order.to_dict(),
            'delivery': delivery.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Pickup error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/mark-in-transit/<order_id>', methods=['POST'])
@jwt_required()
def mark_in_transit(order_id):
    """Mark order as in transit"""
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        delivery = Delivery.query.filter_by(order_id=order_id).first()
        if not delivery or delivery.runner_id != user_id:
            return jsonify({'error': 'Unauthorized or delivery not found'}), 403
        
        delivery.status = 'in_transit'
        order.status = 'in_transit'
        order.in_transit_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"✅ Order {order.order_number} marked in transit")
        
        return jsonify({
            'message': 'Order marked as in transit',
            'order': order.to_dict(),
            'delivery': delivery.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/deliver-order/<order_id>', methods=['POST'])
@jwt_required()
def deliver_order(order_id):
    """Complete delivery and send OTP to customer"""
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        delivery = Delivery.query.filter_by(order_id=order_id).first()
        if not delivery or delivery.runner_id != user_id:
            return jsonify({'error': 'Unauthorized or delivery not found'}), 403
        
        # Generate OTP
        from models import OrderOTP
        from utils import send_email_in_background
        from app import app
        
        otp_obj = OrderOTP.create_for_order(order_id, delivery.id)
        db.session.add(otp_obj)
        db.session.commit()
        
        # Send OTP to customer via email
        customer = User.query.get(order.customer_id)
        if customer and customer.email:
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Order Delivery OTP</h2>
                    <p>Your order <strong>{order.order_number}</strong> has arrived!</p>
                    <p>Please provide this OTP to the delivery person to confirm delivery:</p>
                    <h1 style="color: #ff8c00; letter-spacing: 5px;">{otp_obj.otp}</h1>
                    <p>This OTP is valid for 15 minutes.</p>
                    <p>If you didn't place this order, please contact us immediately.</p>
                </body>
            </html>
            """
            send_email_in_background(
                app=app,
                subject=f"Your Order {order.order_number} Delivery OTP",
                recipients=[customer.email],
                html=html
            )
        
        delivery.status = 'awaiting_otp_verification'
        order.status = 'awaiting_confirmation'
        
        db.session.commit()
        
        print(f"✅ OTP sent for order {order.order_number}: {otp_obj.otp}")
        
        return jsonify({
            'message': 'OTP sent to customer',
            'order': order.to_dict(),
            'delivery': delivery.to_dict(),
            'otp_id': otp_obj.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Delivery error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@runner_bp.route('/confirm-delivery/<order_id>', methods=['POST'])
@jwt_required()
def confirm_delivery(order_id):
    """Confirm delivery with OTP verification"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        otp_code = data.get('otp')
        
        if not otp_code:
            return jsonify({'error': 'OTP required'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        delivery = Delivery.query.filter_by(order_id=order_id).first()
        if not delivery or delivery.runner_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Find OTP
        from models import OrderOTP
        otp_obj = OrderOTP.query.filter_by(
            order_id=order_id,
            delivery_id=delivery.id,
            otp=otp_code
        ).first()
        
        if not otp_obj:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        if otp_obj.is_verified:
            return jsonify({'error': 'OTP already used'}), 400
        
        if datetime.utcnow() > otp_obj.expires_at:
            return jsonify({'error': 'OTP expired'}), 400
        
        # Mark OTP as verified
        otp_obj.is_verified = True
        otp_obj.verified_at = datetime.utcnow()
        
        # Update delivery and order
        delivery.status = 'delivered'
        delivery.actual_delivery_time = datetime.utcnow()
        order.status = 'delivered'
        order.delivered_at = datetime.utcnow()
        
        # Update runner stats
        runner = Runner.query.filter_by(user_id=user_id).first()
        if runner:
            runner.total_deliveries = (runner.total_deliveries or 0) + 1
            runner.status = 'online'
        
        db.session.commit()
        
        print(f"✅ Order {order.order_number} delivered and confirmed!")
        
        return jsonify({
            'message': 'Delivery confirmed successfully',
            'order': order.to_dict(),
            'delivery': delivery.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Confirmation error: {str(e)}")
        return jsonify({'error': str(e)}), 500
