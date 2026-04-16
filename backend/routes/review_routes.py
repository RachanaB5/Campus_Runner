from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid

from backend.models import db, Food, Review, Order, OrderItem

review_bp = Blueprint('review', __name__)


@review_bp.route('', methods=['POST'])
@jwt_required()
def submit_review():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    food_id = data.get('food_id')
    order_id = data.get('order_id')
    try:
        rating = int(data.get('rating', 0))
    except (TypeError, ValueError):
        rating = 0
    comment = (data.get('comment') or '').strip()

    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    if len(comment) > 300:
        return jsonify({'error': 'Comment must be 300 characters or fewer'}), 400
    food = Food.query.get(food_id)
    if not food:
        return jsonify({'error': 'Food not found'}), 404
    order_item = db.session.query(OrderItem).join(Order).filter(
        Order.id == order_id,
        Order.customer_id == user_id,
        OrderItem.food_id == food_id,
        Order.status == 'delivered',
    ).first()
    if not order_item:
        return jsonify({'error': 'You can only review items from your delivered orders'}), 403
    existing_review = Review.query.filter_by(user_id=user_id, food_id=food_id, order_id=order_id).first()
    if existing_review:
        return jsonify({'error': 'You already reviewed this item for this order'}), 409

    review = Review(
        id=str(uuid.uuid4()),
        user_id=user_id,
        food_id=food_id,
        order_id=order_id,
        rating=rating,
        comment=comment,
        is_seeded=False,
    )
    db.session.add(review)
    db.session.flush()

    all_reviews = Review.query.filter_by(food_id=food_id).all()
    rating_count = len(all_reviews)
    food.rating = round(sum(existing.rating for existing in all_reviews) / rating_count, 1) if rating_count else 0
    food.review_count = rating_count
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Review submitted',
        'review': review.to_dict(),
        'new_rating': food.rating,
        'rating_count': food.review_count,
    }), 201


@review_bp.route('/<food_id>', methods=['GET'])
def list_reviews(food_id):
    reviews = Review.query.filter_by(food_id=food_id).order_by(Review.created_at.desc()).all()
    return jsonify({'reviews': [review.to_dict() for review in reviews]}), 200
