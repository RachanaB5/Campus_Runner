from models import db
from datetime import datetime

class RewardPoints(db.Model):
    __tablename__ = 'reward_points'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    total_points = db.Column(db.Integer, default=0)
    points_balance = db.Column(db.Integer, default=0)
    tier = db.Column(db.String(50), default='bronze')  # bronze, silver, gold, platinum
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('RewardTransaction', backref='reward_points', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_points': self.total_points,
            'points_balance': self.points_balance,
            'tier': self.tier,
        }

class RewardTransaction(db.Model):
    __tablename__ = 'reward_transactions'
    
    id = db.Column(db.String(36), primary_key=True)
    reward_points_id = db.Column(db.String(36), db.ForeignKey('reward_points.id'), nullable=False)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'))
    transaction_type = db.Column(db.String(50))  # earned, redeemed
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.transaction_type,
            'transaction_type': self.transaction_type,
            'points': self.points,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
