from models import db
from datetime import datetime

class Food(db.Model):
    __tablename__ = 'foods'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))  # Meals, Biriyanis, Burgers, Beverages, etc.
    image_url = db.Column(db.String(500))
    prep_time = db.Column(db.Integer)  # in minutes
    available = db.Column(db.Boolean, default=True)
    is_veg = db.Column(db.Boolean, default=True)  # True = veg, False = non-veg
    rating = db.Column(db.Float, default=4.5)
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='food', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'prep_time': self.prep_time,
            'available': self.available,
            'is_veg': self.is_veg,
            'rating': self.rating,
            'review_count': self.review_count,
        }