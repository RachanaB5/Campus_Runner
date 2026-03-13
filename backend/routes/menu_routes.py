from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Food
import uuid

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/all', methods=['GET'])
def get_all_foods():
    """Get all available food items"""
    try:
        foods = Food.query.all()
        return jsonify({
            'foods': [food.to_dict() for food in foods]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/search', methods=['GET'])
def search_foods():
    """Search foods by name or category"""
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({'foods': []}), 200
        
        # Search by name or category
        foods = Food.query.filter(
            db.or_(
                Food.name.ilike(f'%{query}%'),
                Food.category.ilike(f'%{query}%'),
                Food.description.ilike(f'%{query}%')
            )
        ).all()
        
        return jsonify({
            'foods': [food.to_dict() for food in foods]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/category/<category>', methods=['GET'])
def get_foods_by_category(category):
    """Get foods by category"""
    try:
        foods = Food.query.filter_by(category=category).all()
        return jsonify({
            'foods': [food.to_dict() for food in foods]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/<food_id>', methods=['GET'])
def get_food_detail(food_id):
    """Get food item details"""
    try:
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404
        return jsonify(food.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/add', methods=['POST'])
@jwt_required()
def add_food():
    """Add new food item (admin only)"""
    try:
        user_id = get_jwt_identity()
        from models import User
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'staff']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        food = Food(
            id=str(uuid.uuid4()),
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            category=data.get('category'),
            image_url=data.get('image_url'),
            prep_time=data.get('prep_time'),
            available=data.get('available', True),
            is_veg=data.get('is_veg', True),
            rating=data.get('rating', 4.5)
        )
        
        db.session.add(food)
        db.session.commit()
        
        return jsonify({
            'message': 'Food added successfully',
            'food': food.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/items/<food_id>', methods=['PUT'])
@jwt_required()
def update_food(food_id):
    """Update food item (admin only)"""
    try:
        user_id = get_jwt_identity()
        from models import User
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'staff']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            food.name = data['name']
        if 'description' in data:
            food.description = data['description']
        if 'price' in data:
            food.price = data['price']
        if 'category' in data:
            food.category = data['category']
        if 'image_url' in data:
            food.image_url = data['image_url']
        if 'prep_time' in data:
            food.prep_time = data['prep_time']
        if 'available' in data:
            food.available = data['available']
        if 'is_veg' in data:
            food.is_veg = data['is_veg']
        if 'rating' in data:
            food.rating = data['rating']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Food updated successfully',
            'food': food.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/items/<food_id>', methods=['DELETE'])
@jwt_required()
def delete_food(food_id):
    """Delete food item (admin only)"""
    try:
        user_id = get_jwt_identity()
        from models import User
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'staff']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404
        
        db.session.delete(food)
        db.session.commit()
        
        return jsonify({'message': 'Food deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
