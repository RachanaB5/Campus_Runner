from . import db
from datetime import datetime
import uuid

class Cart(db.Model):
    __tablename__ = 'carts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    total_price = db.Column(db.Float, default=0.0)
    item_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='cart')
    items = db.relationship('CartItem', backref='cart', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_price': self.total_price,
            'item_count': self.item_count,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id = db.Column(db.String(36), db.ForeignKey('carts.id'), nullable=False)
    food_id = db.Column(db.String(36), db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of adding to cart
    customizations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    food = db.relationship('Food', backref='cart_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'quantity': self.quantity,
            'price': self.price,
            'customizations': self.customizations,
            'total': self.price * self.quantity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
