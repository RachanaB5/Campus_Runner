from models import db
from datetime import datetime

class Delivery(db.Model):
    __tablename__ = 'deliveries'
    
    id = db.Column(db.String(36), primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    runner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='pending')  # pending, assigned, picked_up, in_transit, delivered, failed
    pickup_location = db.Column(db.String(500))
    delivery_location = db.Column(db.String(500))
    distance_km = db.Column(db.Float)
    delivery_fee = db.Column(db.Float)
    estimated_time_minutes = db.Column(db.Integer)
    actual_delivery_time = db.Column(db.DateTime)
    rating = db.Column(db.Float)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'runner_id': self.runner_id,
            'runner_name': self.runner.name if self.runner else None,
            'runner_phone': self.runner.phone if self.runner else None,
            'runner_image': self.runner.profile_image if self.runner else None,
            'status': self.status,
            'pickup_location': self.pickup_location,
            'delivery_location': self.delivery_location,
            'distance_km': self.distance_km,
            'delivery_fee': self.delivery_fee,
            'estimated_time_minutes': self.estimated_time_minutes,
            'actual_delivery_time': self.actual_delivery_time.isoformat() if self.actual_delivery_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'rating': self.rating,
            'review': self.review,
        }
