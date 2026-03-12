from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Order, Food, Delivery
import uuid

staff_admin_bp = Blueprint('staff_admin', __name__)

def check_admin(user_id):
    """Check if user is admin or staff"""
    user = User.query.get(user_id)
    return user and user.role in ['admin', 'staff']

@staff_admin_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        completed_orders = Order.query.filter_by(status='delivered').count()
        total_revenue = sum(order.total_amount for order in Order.query.filter_by(status='delivered').all())
        
        return jsonify({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'total_revenue': total_revenue,
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_admin_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    """Get all orders (admin/staff view)"""
    try:
        user_id = get_jwt_identity()
        
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        status = request.args.get('status')
        
        if status:
            orders = Order.query.filter_by(status=status).all()
        else:
            orders = Order.query.all()
        
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_admin_bp.route('/order/<order_id>/assign-runner', methods=['POST'])
@jwt_required()
def assign_runner_to_order(order_id):
    """Assign a runner to an order"""
    try:
        user_id = get_jwt_identity()
        
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        data = request.get_json()
        runner_id = data.get('runner_id')
        
        # Create or update delivery
        delivery = Delivery.query.filter_by(order_id=order_id).first()
        
        if not delivery:
            delivery = Delivery(
                id=str(uuid.uuid4()),
                order_id=order_id,
                runner_id=runner_id,
                status='assigned'
            )
            db.session.add(delivery)
        else:
            delivery.runner_id = runner_id
            delivery.status = 'assigned'
        
        order.status = 'confirmed'
        db.session.commit()
        
        return jsonify({
            'message': 'Runner assigned to order',
            'delivery': delivery.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_admin_bp.route('/order/<order_id>/mark-ready', methods=['POST'])
@jwt_required()
def mark_order_ready(order_id):
    """Mark order as ready for pickup"""
    try:
        user_id = get_jwt_identity()
        
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order.status = 'ready'
        db.session.commit()
        
        return jsonify({
            'message': 'Order marked as ready',
            'order': order.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (admin only)"""
    try:
        user_id = get_jwt_identity()
        
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        role = request.args.get('role')
        
        if role:
            users = User.query.filter_by(role=role).all()
        else:
            users = User.query.all()
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_admin_bp.route('/user/<user_id>/update-role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        admin_id = get_jwt_identity()
        user = User.query.get(admin_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        target_user = User.query.get(user_id)
        
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        target_user.role = data.get('role')
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated',
            'user': target_user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_admin_bp.route('/foods/inventory', methods=['GET'])
@jwt_required()
def get_foods_inventory():
    """Get food inventory (admin/staff only)"""
    try:
        user_id = get_jwt_identity()
        
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        foods = Food.query.all()
        
        return jsonify({
            'foods': [food.to_dict() for food in foods]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_admin_bp.route('/food/<food_id>/toggle-availability', methods=['POST'])
@jwt_required()
def toggle_food_availability(food_id):
    """Toggle food availability (admin/staff only)"""
    try:
        user_id = get_jwt_identity()
        
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        food = Food.query.get(food_id)
        
        if not food:
            return jsonify({'error': 'Food not found'}), 404
        
        food.available = not food.available
        db.session.commit()
        
        return jsonify({
            'message': 'Food availability toggled',
            'food': food.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_admin_bp.route('/reports/sales', methods=['GET'])
@jwt_required()
def get_sales_report():
    """Get sales report"""
    try:
        user_id = get_jwt_identity()
        
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get completed orders
        completed_orders = Order.query.filter_by(status='delivered').all()
        
        total_sales = sum(order.total_amount for order in completed_orders)
        total_orders = len(completed_orders)
        average_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        return jsonify({
            'total_sales': total_sales,
            'total_orders': total_orders,
            'average_order_value': average_order_value,
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
