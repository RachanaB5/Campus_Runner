"""
One-time cleanup for stale runner and delivery state.

Usage:
  PYTHONPATH=backend .venv/bin/python backend/fix_db.py
"""

from app import app
from models import db, Runner, Order, Delivery


with app.app_context():
    updated_orders = 0

    Runner.query.update({'is_available': False, 'status': 'offline'})

    for delivery in Delivery.query.all():
        order = Order.query.get(delivery.order_id)
        if not order:
            continue

        if delivery.status == 'delivered' and order.status != 'delivered':
            order.status = 'delivered'
            updated_orders += 1
        elif delivery.status in ['picked_up'] and order.status not in ['picked_up', 'in_transit', 'on_the_way', 'delivered']:
            order.status = 'picked_up'
            updated_orders += 1
        elif delivery.status in ['in_transit', 'on_the_way'] and order.status not in ['in_transit', 'on_the_way', 'delivered']:
            order.status = 'on_the_way'
            updated_orders += 1
        elif delivery.status == 'assigned' and order.status in ['pending', 'placed']:
            order.status = 'confirmed'
            updated_orders += 1

    db.session.commit()

    print('Database cleaned up successfully.')
    print(f'Runners reset: {Runner.query.count()}')
    print(f'Orders updated: {updated_orders}')
    print(f'Total orders: {Order.query.count()}')
    print(f'Total deliveries: {Delivery.query.count()}')
