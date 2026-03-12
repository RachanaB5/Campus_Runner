#!/usr/bin/env python3
"""
Initialize the database with sample canteen food data
"""
from app import app
from models import db, User, Food

# Fixed food IDs for consistency
FOOD_IDS = {
    'butter_chicken': 'food-001-butter-chicken-uuid',
    'chicken_biryani': 'food-002-chicken-biryani',
    'paneer_tikka': 'food-003-paneer-tikka-00',
    'veg_fried_rice': 'food-004-veg-fried-rice',
    'chicken_fried_rice': 'food-005-chicken-fried-rice',
    'dal_makhani': 'food-006-dal-makhani-00',
    'aloo_gobi': 'food-007-aloo-gobi-0000',
    'samosa': 'food-008-samosa-0000000',
    'garlic_naan': 'food-009-garlic-naan-00',
    'roti': 'food-010-roti-000000000',
    'coke': 'food-011-coke-25ml-00000',
    'mango_lassi': 'food-012-mango-lassi',
    'gulab_jamun': 'food-013-gulab-jamun-0',
    'ice_cream': 'food-014-ice-cream-000'
}

def init_database():
    """Create all tables and add sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Clear existing foods (optional)
        Food.query.delete()
        
        # Sample canteen food items with fixed IDs
        foods = [
            {
                'id': FOOD_IDS['butter_chicken'],
                'name': 'Butter Chicken',
                'description': 'Tender chicken in creamy tomato-based sauce with butter',
                'price': 240.00,
                'category': 'Main Course',
                'image_url': 'https://images.unsplash.com/photo-1565937539826-b6e9db1b2da1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXR0ZXIlMjBjaGlja2VufGVufDB8fHx8fDE3NzE2NjQyMTR8MA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 25,
                'rating': 4.8
            },
            {
                'id': FOOD_IDS['chicken_biryani'],
                'name': 'Chicken Biryani',
                'description': 'Aromatic basmati rice with tender chicken pieces and spices',
                'price': 200.00,
                'category': 'Main Course',
                'image_url': 'https://images.unsplash.com/photo-1714611626323-5ba6204453be?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiaXJ5YW5pfGVufDB8fHx8fDE3NzE2NjQyMTR8MA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 30,
                'rating': 4.7
            },
            {
                'id': FOOD_IDS['paneer_tikka'],
                'name': 'Paneer Tikka Masala',
                'description': 'Cottage cheese cooked in aromatic tomato and cream sauce',
                'price': 220.00,
                'category': 'Main Course',
                'image_url': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwYW5lZXIlMjB0aWtrYXxlbnwwfHx8fHwxNzcxNjY0MjE0fDA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 25,
                'rating': 4.6
            },
            {
                'id': FOOD_IDS['veg_fried_rice'],
                'name': 'Veg Fried Rice',
                'description': 'Fragrant basmati rice stir-fried with fresh vegetables and soy sauce',
                'price': 140.00,
                'category': 'Rice',
                'image_url': 'https://images.unsplash.com/photo-1609501676725-7186f017a4b0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx2ZWclMjBmcmllZCUyMHJpY2V8ZW58MHx8fHx8MTc3MTY2NDIxNHww&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 15,
                'rating': 4.5
            },
            {
                'id': FOOD_IDS['chicken_fried_rice'],
                'name': 'Chicken Fried Rice',
                'description': 'Basmati rice with tender chicken pieces and stir-fried vegetables',
                'price': 180.00,
                'category': 'Rice',
                'image_url': 'https://images.unsplash.com/photo-1609501676725-7186f017a4b0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjaGlja2VuJTIwZnJpZWQlMjByaWNlfGVufDB8fHx8fDE3NzE2NjQyMTR8MA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 18,
                'rating': 4.6
            },
            {
                'id': FOOD_IDS['dal_makhani'],
                'name': 'Dal Makhani',
                'description': 'Slow-cooked black lentils with cream and aromatic spices',
                'price': 130.00,
                'category': 'Vegetarian',
                'image_url': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkYWwlMjBtYWtoYW5pfGVufDB8fHx8fDE3NzE2NjQyMTR8MA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 20,
                'rating': 4.5
            },
            {
                'id': FOOD_IDS['aloo_gobi'],
                'name': 'Aloo Gobi',
                'description': 'Potatoes and cauliflower cooked with fresh ginger and spices',
                'price': 110.00,
                'category': 'Vegetarian',
                'image_url': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhbG9vJTIwZ29iaXxlbnwwfHx8fHwxNzcxNjY0MjE0fDA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 18,
                'rating': 4.4
            },
            {
                'id': FOOD_IDS['samosa'],
                'name': 'Samosa (4 pcs)',
                'description': 'Crispy fried pastry filled with spiced potatoes and peas',
                'price': 50.00,
                'category': 'Appetizers',
                'image_url': 'https://images.unsplash.com/photo-1599599810694-b5ac4dd97a2f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzYW1vc2F8ZW58MHx8fHx8MTc3MTY2NDIxNHww&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 10,
                'rating': 4.3
            },
            {
                'id': FOOD_IDS['garlic_naan'],
                'name': 'Garlic Naan',
                'description': 'Soft Indian flatbread baked in tandoor with garlic and butter',
                'price': 60.00,
                'category': 'Bread',
                'image_url': 'https://images.unsplash.com/photo-1585238341710-4913968ba8f7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxuYWFufGVufDB8fHx8fDE3NzE2NjQyMTR8MA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 8,
                'rating': 4.7
            },
            {
                'id': FOOD_IDS['roti'],
                'name': 'Roti',
                'description': 'Traditional Indian wheat flatbread',
                'price': 30.00,
                'category': 'Bread',
                'image_url': 'https://images.unsplash.com/photo-1585238341710-4913968ba8f7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb3RpfGVufDB8fHx8fDE3NzE2NjQyMTR8MA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 5,
                'rating': 4.5
            },
            {
                'id': FOOD_IDS['coke'],
                'name': 'Coke (250ml)',
                'description': 'Cold carbonated beverage',
                'price': 30.00,
                'category': 'Beverages',
                'image_url': 'https://images.unsplash.com/photo-1554866585-b92e5a1c0f5f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2xkJTIwZHJpbmt8ZW58MHx8fHx8MTc3MTY2NDIxNHww&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 2,
                'rating': 4.4
            },
            {
                'id': FOOD_IDS['mango_lassi'],
                'name': 'Mango Lassi',
                'description': 'Fresh mango yogurt smoothie',
                'price': 80.00,
                'category': 'Beverages',
                'image_url': 'https://images.unsplash.com/photo-1582735689369-e68a7d48b69e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsYXNzaXxlbnwwfHx8fHwxNzcxNjY0MjE0fDA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 5,
                'rating': 4.6
            },
            {
                'id': FOOD_IDS['gulab_jamun'],
                'name': 'Gulab Jamun (4 pcs)',
                'description': 'Soft milk solids dumplings soaked in sugar syrup',
                'price': 70.00,
                'category': 'Desserts',
                'image_url': 'https://images.unsplash.com/photo-1585518419759-e32068c83056?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkZXNzZXJ0fGVufDB8fHx8fDE3NzE2NjQyMTR8MA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 5,
                'rating': 4.7
            },
            {
                'id': FOOD_IDS['ice_cream'],
                'name': 'Ice Cream (Vanilla/Chocolate)',
                'description': 'Creamy ice cream in vanilla or chocolate flavor',
                'price': 50.00,
                'category': 'Desserts',
                'image_url': 'https://images.unsplash.com/photo-1585518419759-e32068c83056?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpY2UlMjBjcmVhbXxlbnwwfHx8fHwxNzcxNjY0MjE0fDA&ixlib=rb-4.1.0&q=80&w=1080',
                'prep_time': 2,
                'rating': 4.5
            }
        ]
        
        # Add foods to database
        for food_data in foods:
            food = Food(
                **food_data,
                available=True,
                review_count=int(food_data['rating'] * 10)
            )
            db.session.add(food)
        
        db.session.commit()
        print(f"✓ Added {len(foods)} food items to database")
        
        # Display added items
        all_foods = Food.query.all()
        print(f"\nCanteen Menu ({len(all_foods)} items):")
        print("-" * 60)
        for food in all_foods:
            print(f"  {food.name:30} | ₹{food.price:6.2f} | {food.prep_time}min | ⭐{food.rating}")
        print("-" * 60)
        print("\n✓ Database initialization complete!")

if __name__ == '__main__':
    init_database()
