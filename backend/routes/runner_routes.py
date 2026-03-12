from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Runner, Delivery, Order
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

from datetime import datetime
