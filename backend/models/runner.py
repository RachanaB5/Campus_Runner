from . import db
from datetime import datetime

class Runner(db.Model):
    __tablename__ = 'runners'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    vehicle_type = db.Column(db.String(50))  # bike, scooter, bicycle
    license_number = db.Column(db.String(100), unique=True)
    is_available = db.Column(db.Boolean, default=True)
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)
    total_deliveries = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    total_earnings = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='offline')  # online, offline, on_delivery
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'vehicle_type': self.vehicle_type,
            'license_number': self.license_number,
            'is_available': self.is_available,
            'current_latitude': self.current_latitude,
            'current_longitude': self.current_longitude,
            'total_deliveries': self.total_deliveries,
            'average_rating': self.average_rating,
            'total_earnings': self.total_earnings,
            'status': self.status,
        }
