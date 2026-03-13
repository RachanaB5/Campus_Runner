from models import db
from datetime import datetime
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(50), default='customer')  # customer, runner, staff, admin
    profile_image = db.Column(db.String(500))
    wallet_balance = db.Column(db.Float, default=0.0)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', foreign_keys='Order.customer_id')
    runner_deliveries = db.relationship('Delivery', backref='runner', foreign_keys='Delivery.runner_id')
    reward_points = db.relationship('RewardPoints', backref='user', uselist=False)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'profile_image': self.profile_image,
            'wallet_balance': self.wallet_balance,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
