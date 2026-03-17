from models import db
from datetime import datetime, timedelta
import random
import string

class OrderOTP(db.Model):
    __tablename__ = 'order_otps'
    
    id = db.Column(db.String(36), primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    delivery_id = db.Column(db.String(36), db.ForeignKey('deliveries.id'), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='otps')
    delivery = db.relationship('Delivery', backref='otps')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'delivery_id': self.delivery_id,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_for_order(order_id, delivery_id):
        """Create OTP for delivery verification"""
        otp = OrderOTP.generate_otp()
        order_otp = OrderOTP(
            id=str(__import__('uuid').uuid4()),
            order_id=order_id,
            delivery_id=delivery_id,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        return order_otp
