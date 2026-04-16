from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, Food, User
from backend.models.cart import Cart, CartItem
import uuid

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    """Get user's cart"""
    try:
        user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=user_id).first()
        
        if not cart:
            # Create a new cart if user doesn't have one
            cart = Cart(id=str(uuid.uuid4()), user_id=user_id)
            db.session.add(cart)
            db.session.commit()
        
        return jsonify(cart.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add item to cart"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        food_id = data.get('food_id')
        quantity = data.get('quantity', 1)
        customizations = data.get('customizations')
        
        if not food_id or quantity < 1:
            return jsonify({'error': 'Invalid food_id or quantity'}), 400
        
        # Get food item
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food item not found'}), 404
        
        # Get or create cart
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(id=str(uuid.uuid4()), user_id=user_id)
            db.session.add(cart)
            db.session.flush()  # Flush to get the cart ID if needed
        
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(cart_id=cart.id, food_id=food_id, customizations=customizations).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
        else:
            # Add new item
            cart_item = CartItem(
                id=str(uuid.uuid4()),
                cart_id=cart.id,
                food_id=food_id,
                quantity=quantity,
                price=food.price,
                customizations=customizations,
            )
            db.session.add(cart_item)
        
        # Update cart totals
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        cart.item_count = sum(item.quantity for item in cart_items) if cart_items else 0
        cart.total_price = sum(item.price * item.quantity for item in cart_items) if cart_items else 0.0
        
        db.session.commit()
        
        return jsonify({
            'message': 'Item added to cart',
            'cart': cart.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/item/<item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        user_id = get_jwt_identity()
        
        # Verify the item belongs to user's cart
        cart_item = CartItem.query.get(item_id)
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        cart = cart_item.cart
        if cart.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(cart_item)
        
        # Update cart totals
        remaining_items = CartItem.query.filter_by(cart_id=cart.id).all()
        cart.item_count = len(remaining_items)
        cart.total_price = sum(item.price * item.quantity for item in remaining_items) if remaining_items else 0.0
        
        db.session.commit()
        
        return jsonify({
            'message': 'Item removed from cart',
            'cart': cart.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/item/<item_id>', methods=['PATCH', 'PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        quantity = data.get('quantity')
        customizations = data.get('customizations')
        if quantity is None or quantity < 1:
            return jsonify({'error': 'Invalid quantity'}), 400
        
        # Verify the item belongs to user's cart
        cart_item = CartItem.query.get(item_id)
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        cart = cart_item.cart
        if cart.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        cart_item.quantity = quantity
        if customizations is not None:
            cart_item.customizations = customizations
        
        # Update cart totals
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        cart.item_count = sum(item.quantity for item in cart_items) if cart_items else 0
        cart.total_price = sum(item.price * item.quantity for item in cart_items) if cart_items else 0.0
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cart item updated',
            'cart': cart.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from cart"""
    try:
        user_id = get_jwt_identity()
        
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404
        
        # Delete all cart items
        CartItem.query.filter_by(cart_id=cart.id).delete()
        
        # Reset cart totals
        cart.item_count = 0
        cart.total_price = 0.0
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cart cleared',
            'cart': cart.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout_cart():
    """Convert cart to order"""
    try:
        user_id = get_jwt_identity()
        
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # This will be implemented with Order model integration
        # For now, we'll just return success
        return jsonify({
            'message': 'Checkout initiated',
            'total': cart.total_price,
            'items_count': cart.item_count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
