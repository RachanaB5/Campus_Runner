from __future__ import annotations

from datetime import datetime
import uuid

from models import db, Notification, Order, Runner, User


def calculate_runner_reward(order_total: float) -> int:
    return max(10, int(round(float(order_total or 0) / 15)))


def _wants_notification(user_id: str, pref_key: str) -> bool:
    user = User.query.get(user_id)
    prefs = user.notification_preferences if user else None
    if not prefs:
        return True
    return prefs.get(pref_key, True)


def create_notification(user_id: str, title: str, body: str, notification_type: str = 'system', related_id: str | None = None, action_url: str | None = None) -> Notification:
    notification = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        body=body,
        type=notification_type,
        related_id=related_id,
        action_url=action_url,
    )
    db.session.add(notification)
    return notification


def emit_to_user(user_id: str, event_name: str, payload: dict) -> None:
    try:
        import app as app_module

        if getattr(app_module, 'socketio', None):
            app_module.socketio.emit(event_name, payload, room=f'user:{user_id}')
    except Exception:
        return


def notify_runners_new_order(order: Order) -> None:
    items = order.items or []
    first_item = items[0].food if items else None
    pickup_location = getattr(first_item, 'counter_number', None) or 'Campus kitchen'
    reward_points = calculate_runner_reward(order.total_amount)
    payload = {
        'event': 'new_order',
        'order_id': order.id,
        'order_number': order.order_number,
        'token_number': order.order_number,
        'pickup_location': f'Counter {pickup_location}' if str(pickup_location).isdigit() else str(pickup_location),
        'delivery_location': order.delivery_address,
        'item_count': len(items),
        'items_summary': [item.food.name for item in items[:3] if item.food],
        'reward_points': reward_points,
        'estimated_prep_time': max([getattr(item.food, 'prep_time', 0) or 0 for item in items], default=15),
        'placed_at': order.created_at.isoformat() if order.created_at else datetime.utcnow().isoformat(),
        'distance_estimate': '~200m',
    }

    available_runners = Runner.query.filter_by(is_available=True).all()
    for runner in available_runners:
        if runner.user_id == order.customer_id:
            continue
        if _wants_notification(runner.user_id, 'new_orders_available'):
            create_notification(
                user_id=runner.user_id,
                title='New Order Available',
                body=f'{payload["item_count"]} item(s) ready to claim. Earn {reward_points} pts.',
                notification_type='new_order',
                related_id=order.id,
                action_url='/runner',
            )

    customer_notification = None
    if _wants_notification(order.customer_id, 'order_updates'):
        customer_notification = create_notification(
            user_id=order.customer_id,
            title='Order Confirmed',
            body=f'Your order {order.order_number} is confirmed and runners are being notified.',
            notification_type='order_update',
            related_id=order.id,
            action_url='/orders',
        )

    try:
        import app as app_module

        if getattr(app_module, 'socketio', None):
            app_module.socketio.emit('new_order_available', payload, room='runners_online')
            app_module.socketio.emit('notification:new', payload, room='runners_online')
            if customer_notification:
                app_module.socketio.emit('notification:new', customer_notification.to_dict(), room=f'user:{order.customer_id}')
    except Exception:
        pass

    db.session.commit()


def notify_order_taken(order: Order, runner_user: User) -> None:
    try:
        import app as app_module

        payload = {
            'order_id': order.id,
            'order_number': order.order_number,
            'runner_name': runner_user.name if runner_user else 'Runner',
            'message': 'Your order has been accepted by a runner.',
        }

        if getattr(app_module, 'socketio', None):
            app_module.socketio.emit('order_taken', {'order_id': order.id}, room='runners_online')
            app_module.socketio.emit('order_accepted', payload, room=f'user:{order.customer_id}')

        notification = None
        if _wants_notification(order.customer_id, 'runner_assigned'):
            notification = create_notification(
                user_id=order.customer_id,
                title='Runner Assigned',
                body=f'{payload["runner_name"]} accepted your order {order.order_number}.',
                notification_type='order_accepted',
                related_id=order.id,
                action_url='/orders',
            )
        if getattr(app_module, 'socketio', None) and notification:
            app_module.socketio.emit('notification:new', notification.to_dict(), room=f'user:{order.customer_id}')
        db.session.commit()
    except Exception:
        db.session.rollback()
