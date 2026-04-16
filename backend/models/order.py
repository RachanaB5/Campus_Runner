from . import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(50), default='pending')  # pending, received, preparing, ready, picked_up, in_transit, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    payment_method = db.Column(db.String(50))  # card, upi, wallet, cash
    delivery_address = db.Column(db.Text)
    customer_phone = db.Column(db.String(20))
    special_instructions = db.Column(db.Text)
    estimated_delivery_time = db.Column(db.DateTime)
    
    # Tracking timestamps
    received_by_canteen_at = db.Column(db.DateTime)  # When canteen receives order
    preparation_started_at = db.Column(db.DateTime)  # When canteen starts preparing
    ready_for_pickup_at = db.Column(db.DateTime)  # When order is ready
    picked_up_at = db.Column(db.DateTime)  # When runner picks up
    in_transit_at = db.Column(db.DateTime)  # When runner starts delivery
    delivered_at = db.Column(db.DateTime)  # When order is delivered
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')
    delivery = db.relationship('Delivery', backref='order', uselist=False)
    
    def to_dict(self, include_items=True, include_delivery=True):
        order_dict = {
            'id': self.id,
            'customer_id': self.customer_id,
            'order_number': self.order_number,
            'status': self.status,
            'total_amount': self.total_amount,
            'delivery_fee': self.delivery_fee,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'delivery_address': self.delivery_address,
            'customer_phone': self.customer_phone,
            'special_instructions': self.special_instructions,
            'estimated_delivery_time': self.estimated_delivery_time.isoformat() if self.estimated_delivery_time else None,
            'tracking': {
                'received_by_canteen_at': self.received_by_canteen_at.isoformat() if self.received_by_canteen_at else None,
                'preparation_started_at': self.preparation_started_at.isoformat() if self.preparation_started_at else None,
                'ready_for_pickup_at': self.ready_for_pickup_at.isoformat() if self.ready_for_pickup_at else None,
                'picked_up_at': self.picked_up_at.isoformat() if self.picked_up_at else None,
                'in_transit_at': self.in_transit_at.isoformat() if self.in_transit_at else None,
                'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_items and self.items:
            order_dict['items'] = [item.to_dict() for item in self.items]
        if include_delivery and self.delivery:
            order_dict['delivery'] = self.delivery.to_dict()
        return order_dict

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.String(36), primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    food_id = db.Column(db.String(36), db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    customizations = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'customizations': self.customizations,
        }
