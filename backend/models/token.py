from models import db
from datetime import datetime

class Token(db.Model):
    __tablename__ = 'tokens'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    token_number = db.Column(db.String(50), unique=True, nullable=False)
    counter = db.Column(db.String(50))
    sequence = db.Column(db.Integer)
    status = db.Column(db.String(50), default='pending')  # pending, called, completed
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'))
    called_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token_number': self.token_number,
            'counter': self.counter,
            'sequence': self.sequence,
            'status': self.status,
            'order_id': self.order_id,
            'called_at': self.called_at.isoformat() if self.called_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
