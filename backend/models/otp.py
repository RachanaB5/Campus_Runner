from models import db
from datetime import datetime, timedelta
import uuid
import secrets
class OrderOTP(db.Model):
    __tablename__ = 'order_otps'
    
    id = db.Column(db.String(36), primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    delivery_id = db.Column(db.String(36), db.ForeignKey('deliveries.id'), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    otp_type = db.Column(db.String(20), default='delivery')
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
            'otp_type': self.otp_type,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    @staticmethod
    def generate_otp():
        """Generate a 4-digit OTP using secrets for cryptographic randomness"""
        import secrets
        return ''.join(secrets.choice('0123456789') for _ in range(4))
    
    @staticmethod
    def create_for_order(order_id, delivery_id, otp_type='delivery'):
        """Create OTP for pickup or delivery verification"""
        otp = OrderOTP.generate_otp()
        order_otp = OrderOTP(
            id=str(uuid.uuid4()),
            order_id=order_id,
            delivery_id=delivery_id,
            otp=otp,
            otp_type=otp_type,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        return order_otp
