from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Runner, Delivery, Order
from datetime import datetime
import uuid

runner_bp = Blueprint('runner', __name__)

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
            is_available=True,
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
        
        delivery = Delivery.query.get(delivery_id)
        
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        
        if delivery.runner_id:
            return jsonify({'error': 'Delivery already assigned'}), 400
        
        delivery.runner_id = user_id
        delivery.status = 'assigned'
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
    """Get orders ready for pickup by runner"""
    try:
        user_id = get_jwt_identity()
        runner = Runner.query.filter_by(user_id=user_id).first()
        
        if not runner:
            return jsonify({'error': 'Runner profile not found'}), 404
        
        # Get orders that are ready for pickup and don't have delivery yet
        ready_orders = Order.query.filter_by(status='ready').all()
        
        orders_data = []
        for order in ready_orders:
            if not order.delivery:  # Only show if no delivery assigned
                order_dict = order.to_dict(include_items=True)
                customer = User.query.get(order.customer_id)
                order_dict['customer_name'] = customer.name if customer else 'Unknown'
                order_dict['customer_phone'] = order.customer_phone
                orders_data.append(order_dict)
        
        return jsonify({
            'available_orders': orders_data,
            'count': len(orders_data)
        }), 200
    
    except Exception as e:
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

