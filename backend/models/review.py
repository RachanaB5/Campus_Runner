from datetime import datetime

from models import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    food_id = db.Column(db.String(36), db.ForeignKey('foods.id'), nullable=False, index=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    is_seeded = db.Column(db.Boolean, default=False)
    seeded_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='reviews')
    food = db.relationship('Food', backref='reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'food_id': self.food_id,
            'order_id': self.order_id,
            'rating': self.rating,
            'comment': self.comment,
            'is_seeded': self.is_seeded,
            'seeded_name': self.seeded_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
