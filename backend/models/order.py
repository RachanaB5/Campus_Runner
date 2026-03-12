from models import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, preparing, ready, picked_up, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    payment_method = db.Column(db.String(50))  # card, upi, wallet, cash
    delivery_address = db.Column(db.Text)
    customer_phone = db.Column(db.String(20))
    special_instructions = db.Column(db.Text)
    estimated_delivery_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')
    delivery = db.relationship('Delivery', backref='order', uselist=False)
    
    def to_dict(self, include_items=True):
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_items and self.items:
            order_dict['items'] = [item.to_dict() for item in self.items]
        return order_dict

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.String(36), primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    food_id = db.Column(db.String(36), db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
        }
