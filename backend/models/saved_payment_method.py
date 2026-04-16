from datetime import datetime

from . import db


class SavedPaymentMethod(db.Model):
    __tablename__ = 'saved_payment_methods'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)  # card / upi
    upi_id = db.Column(db.String(100))
    upi_nickname = db.Column(db.String(50))
    card_last4 = db.Column(db.String(4))
    card_holder_name = db.Column(db.String(100))
    card_expiry = db.Column(db.String(7))
    card_brand = db.Column(db.String(20))
    card_number_hash = db.Column(db.String(200))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='saved_payment_methods')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'upi_id': self.upi_id,
            'upi_nickname': self.upi_nickname,
            'card_last4': self.card_last4,
            'card_holder_name': self.card_holder_name,
            'card_expiry': self.card_expiry,
            'card_brand': self.card_brand,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
