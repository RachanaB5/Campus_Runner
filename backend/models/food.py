from models import db
from datetime import datetime

DEFAULT_FOOD_IMAGES = {
    'meals': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop',
    'combos': 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400&h=300&fit=crop',
    'north indian': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop',
    'parathas': 'https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=300&fit=crop',
    'rolls': 'https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=300&fit=crop',
    'biryanis': 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&h=300&fit=crop',
    'biryani': 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&h=300&fit=crop',
    'burgers': 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=400&h=300&fit=crop',
    'maggi': 'https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=400&h=300&fit=crop',
    'pizzas': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop',
    'beverages': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop',
    'soda': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop',
    'lassi': 'https://images.unsplash.com/photo-1582735689369-e68a7d48b69e?w=400&h=300&fit=crop',
    'milk shakes': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=300&fit=crop',
    'ice cream': 'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=400&h=300&fit=crop',
    'desserts': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop',
}

FALLBACK_FOOD_IMAGE = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop'


def get_default_food_image(category):
    if not category:
        return FALLBACK_FOOD_IMAGE
    return DEFAULT_FOOD_IMAGES.get(category.strip().lower(), FALLBACK_FOOD_IMAGE)


class Food(db.Model):
    __tablename__ = 'foods'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))  # Meals, Biriyanis, Burgers, Beverages, etc.
    image_url = db.Column(db.String(500))
    prep_time = db.Column(db.Integer)  # in minutes
    calories = db.Column(db.Integer)
    ingredients = db.Column(db.Text)
    counter_number = db.Column(db.Integer)
    counter_name = db.Column(db.String(255))
    available = db.Column(db.Boolean, default=True)
    is_veg = db.Column(db.Boolean, default=True)  # True = veg, False = non-veg
    rating = db.Column(db.Float, default=4.5)
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='food', cascade='all, delete-orphan')
    
    def to_dict(self):
        image_url = self.image_url or get_default_food_image(self.category)
        ingredients = [part.strip() for part in (self.ingredients or '').split(',') if part.strip()]
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': image_url,
            'prep_time': self.prep_time,
            'prep_time_mins': self.prep_time,
            'calories': self.calories,
            'ingredients': ingredients,
            'counter_number': self.counter_number,
            'counter_name': self.counter_name,
            'available': self.available,
            'is_available': self.available,
            'is_veg': self.is_veg,
            'rating': self.rating,
            'review_count': self.review_count,
            'rating_count': self.review_count,
        }
