from . import db
from datetime import datetime
import re

class Checkout(db.Model):
    __tablename__ = 'checkouts'
    
    id = db.Column(db.String(36), primary_key=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), unique=True, nullable=True)
    
    # Delivery Information
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_city = db.Column(db.String(100), nullable=False)
    delivery_pincode = db.Column(db.String(10), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    
    # Validation Flags
    is_address_valid = db.Column(db.Boolean, default=False)
    is_phone_valid = db.Column(db.Boolean, default=False)
    is_payment_method_selected = db.Column(db.Boolean, default=False)
    is_items_available = db.Column(db.Boolean, default=False)
    
    # Additional Information
    special_instructions = db.Column(db.Text)
    payment_method = db.Column(db.String(50))  # cash, card, upi, wallet
    estimated_delivery_time = db.Column(db.DateTime)
    discount_code = db.Column(db.String(50))
    discount_amount = db.Column(db.Float, default=0.0)
    
    # Totals
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, nullable=False)
    final_total = db.Column(db.Float, nullable=False)
    
    # Status
    checkout_status = db.Column(db.String(50), default='pending')  # pending, confirmed, cancelled
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def validate_all(self):
        """Validate all checkout fields"""
        self.is_address_valid = self.validate_address()
        self.is_phone_valid = self.validate_phone()
        self.is_payment_method_selected = bool(self.payment_method)
        return self.is_all_valid()
    
    def validate_address(self):
        """Validate delivery address"""
        if not self.delivery_address or len(self.delivery_address.strip()) < 10:
            return False
        if not self.delivery_city or len(self.delivery_city.strip()) < 2:
            return False
        if not self.delivery_pincode or not re.match(r'^\d{5,6}$', self.delivery_pincode.strip()):
            return False
        return True
    
    def validate_phone(self):
        """Validate phone number"""
        if not self.customer_phone:
            return False
        phone = re.sub(r'\D', '', self.customer_phone)
        return bool(re.match(r'^\d{10}$', phone))
    
    def is_all_valid(self):
        """Check if all validations pass"""
        return (
            self.is_address_valid and 
            self.is_phone_valid and 
            self.is_payment_method_selected and 
            self.is_items_available
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'order_id': self.order_id,
            'delivery_address': self.delivery_address,
            'delivery_city': self.delivery_city,
            'delivery_pincode': self.delivery_pincode,
            'customer_phone': self.customer_phone,
            'is_address_valid': self.is_address_valid,
            'is_phone_valid': self.is_phone_valid,
            'is_payment_method_selected': self.is_payment_method_selected,
            'is_items_available': self.is_items_available,
            'is_all_valid': self.is_all_valid(),
            'special_instructions': self.special_instructions,
            'payment_method': self.payment_method,
            'estimated_delivery_time': self.estimated_delivery_time.isoformat() if self.estimated_delivery_time else None,
            'discount_code': self.discount_code,
            'discount_amount': self.discount_amount,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'delivery_fee': self.delivery_fee,
            'final_total': self.final_total,
            'checkout_status': self.checkout_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
