from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, Food, Review
import uuid

menu_bp = Blueprint('menu', __name__)

CATEGORY_ALIASES = {
    'biryani': ['Biryani', 'Biryanis'],
    'biryanis': ['Biryani', 'Biryanis'],
    'pizza': ['Pizzas', 'Pizza & Bread'],
    'pizzas': ['Pizzas', 'Pizza & Bread'],
    'beverages': ['Cold Drinks', 'Tea & Coffee', 'Other Drinks', 'Fresh Juices', 'Soda', 'Lassi', 'Smooth Drinks', 'Special Shakes', 'Paper Boat', 'Tropicana', 'Milk Shakes'],
}

COUNTER_MAP = {
    'Biryanis': ('Biryani & Rice Counter', 3),
    'Meals': ('Meals Counter', 1),
    'North Indian': ('North Indian Counter', 2),
    'Parathas': ('North Indian Counter', 2),
    'Pizzas': ('Pizza Counter', 5),
    'Pasta': ('Pasta Counter', 6),
    'Rolls': ('Rolls & Wraps Counter', 4),
    'Burgers': ('Fast Food Counter', 4),
    'Combos': ('Combo Counter', 2),
}


def _food_detail_defaults(food):
    category = food.category or 'Meals'
    counter_name, counter_number = COUNTER_MAP.get(category, ('Main Counter', 1))
    ingredients = [part.strip() for part in (food.ingredients or '').split(',') if part.strip()]
    if not ingredients:
        ingredients = [category, 'Campus spice mix', 'Fresh herbs']
    return {
        'ingredients': ingredients,
        'calories': food.calories or int(float(food.price or 50) * 5),
        'counter_number': food.counter_number or counter_number,
        'counter_name': food.counter_name or counter_name,
    }


def _review_payload(review):
    user_name = review.seeded_name if getattr(review, 'is_seeded', False) and review.seeded_name else (review.user.name if review.user else 'Campus User')
    parts = user_name.split()
    display_name = parts[0] if parts else 'Campus'
    if len(parts) > 1:
        display_name = f'{parts[0]} {parts[-1][0]}.'
    return {
        'review_id': review.id,
        'user_initial': user_name[:1].upper(),
        'user_name': display_name,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.isoformat() if review.created_at else None,
        'order_id': review.order_id,
        'is_seeded': getattr(review, 'is_seeded', False),
    }

@menu_bp.route('/all', methods=['GET'])
def get_all_foods():
    """Get all available food items"""
    try:
        foods = Food.query.filter_by(available=True).all()
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
            ),
            Food.available.is_(True)
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
        category_key = (category or '').strip()
        normalized_aliases = CATEGORY_ALIASES.get(category_key.lower(), [category_key])
        foods = Food.query.filter(Food.category.in_(normalized_aliases), Food.available.is_(True)).all()
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
        reviews = Review.query.filter_by(food_id=food_id).order_by(Review.created_at.desc()).all()
        rating_distribution = {str(star): 0 for star in range(1, 6)}
        for review in reviews:
            rating_distribution[str(review.rating)] += 1
        payload = food.to_dict()
        payload.update(_food_detail_defaults(food))
        payload['reviews'] = [_review_payload(review) for review in reviews[:10]]
        payload['rating_distribution'] = rating_distribution
        return jsonify(payload), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/add', methods=['POST'])
@menu_bp.route('', methods=['POST'])
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
@menu_bp.route('/<food_id>', methods=['PUT'])
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
@menu_bp.route('/<food_id>', methods=['DELETE'])
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
        
        from models import CartItem
        CartItem.query.filter_by(food_id=food_id).delete(synchronize_session=False)
        db.session.delete(food)
        db.session.commit()
        
        return jsonify({'message': 'Food deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
