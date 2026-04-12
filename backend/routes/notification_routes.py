from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Notification, db

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('', methods=['GET'])
@jwt_required()
def list_notifications():
    user_id = get_jwt_identity()
    unread_only = (request.args.get('unread') or '').lower() == 'true'
    limit = min(int(request.args.get('limit', 20)), 50)
    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    return jsonify({
        'notifications': [notification.to_dict() for notification in notifications],
        'unread_count': Notification.query.filter_by(user_id=user_id, is_read=False).count(),
    }), 200


@notification_bp.route('/<notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_one_read(notification_id):
    user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read', 'notification': notification.to_dict()}), 200


@notification_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    user_id = get_jwt_identity()
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'Notifications marked as read'}), 200
