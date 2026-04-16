from datetime import datetime

from . import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.String(36), primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), index=True)
    method = db.Column(db.String(20), default='upi')
    razorpay_order_id = db.Column(db.String(120), index=True)
    razorpay_payment_id = db.Column(db.String(120), index=True)
    razorpay_signature = db.Column(db.String(255))
    upi_id = db.Column(db.String(120))
    card_last4 = db.Column(db.String(4))
    card_number_hash = db.Column(db.String(255))
    card_holder_name = db.Column(db.String(120))
    card_expiry = db.Column(db.String(7))
    amount = db.Column(db.Integer, nullable=False)  # Amount in paise
    currency = db.Column(db.String(10), default='INR')
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = db.relationship('Order', backref='payments')
    user = db.relationship('User', backref='payments')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'method': self.method,
            'razorpay_order_id': self.razorpay_order_id,
            'razorpay_payment_id': self.razorpay_payment_id,
            'upi_id': self.upi_id,
            'card_last4': self.card_last4,
            'card_holder_name': self.card_holder_name,
            'card_expiry': self.card_expiry,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
