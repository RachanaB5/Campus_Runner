from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import os
import sys

# Ensure we're in the right directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(backend_dir)

# Load environment variables from parent directory (.env file location)
dotenv_path = os.path.join(parent_dir, '.env')
print(f"\n📂 Backend directory: {backend_dir}")
print(f"📂 Parent directory: {parent_dir}")
print(f"📂 Looking for .env at: {dotenv_path}")
print(f"📂 .env exists: {os.path.exists(dotenv_path)}")

load_dotenv(dotenv_path)

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///campusrunner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

# Email Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@campusrunner.com')

# Initialize extensions
from models import db
db.init_app(app)

CORS(app)
jwt = JWTManager(app)

# Initialize Flask-Mail
mail = Mail()
mail.init_app(app)

# Print email configuration for debugging
with app.app_context():
    print(f"\n=== EMAIL CONFIGURATION ===")
    print(f"Mail Server: {app.config.get('MAIL_SERVER')}")
    print(f"Mail Port: {app.config.get('MAIL_PORT')}")
    print(f"Mail Username: {app.config.get('MAIL_USERNAME')}")
    print(f"Mail TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"Mail Has Password: {'Yes' if app.config.get('MAIL_PASSWORD') else 'No'}")
    print(f"===========================\n")

# Register blueprints (routes)
from routes.auth_routes import auth_bp
from routes.menu_routes import menu_bp
from routes.order_routes import order_bp
from routes.runner_routes import runner_bp
from routes.staff_admin_routes import staff_admin_bp
from routes.cart_routes import cart_bp
from routes.checkout_routes import checkout_bp
from routes.rewards_routes import rewards_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(menu_bp, url_prefix='/api/menu')
app.register_blueprint(order_bp, url_prefix='/api/order')
app.register_blueprint(checkout_bp, url_prefix='/api/checkout')
app.register_blueprint(runner_bp, url_prefix='/api/runner')
app.register_blueprint(rewards_bp, url_prefix='/api/rewards')
app.register_blueprint(staff_admin_bp, url_prefix='/api/admin')
app.register_blueprint(cart_bp, url_prefix='/api/cart')

# Create tables
with app.app_context():
    db.create_all()
    # Auto-initialize database on app startup if empty
    from models import Food
    if Food.query.count() == 0:
        foods_data = [
            # MEALS
            {'name': 'North Mini Meals', 'price': 70, 'category': 'Meals', 'is_veg': True, 'prep_time': 20, 'rating': 4.5},
            {'name': 'North Full Meals', 'price': 120, 'category': 'Meals', 'is_veg': True, 'prep_time': 25, 'rating': 4.6},
            {'name': 'South Mini Meals', 'price': 50, 'category': 'Meals', 'is_veg': True, 'prep_time': 20, 'rating': 4.4},
            {'name': 'South Full Meals', 'price': 100, 'category': 'Meals', 'is_veg': True, 'prep_time': 25, 'rating': 4.5},
            
            # COMBOS
            {'name': 'Jeera Rice with Dal Tadka', 'price': 70, 'category': 'Combos', 'is_veg': True, 'prep_time': 20, 'rating': 4.5},
            {'name': 'Rajma / Chole Rice', 'price': 70, 'category': 'Combos', 'is_veg': True, 'prep_time': 20, 'rating': 4.4},
            {'name': 'Aloo Paratha with Chole', 'price': 80, 'category': 'Combos', 'is_veg': True, 'prep_time': 20, 'rating': 4.6},
            {'name': 'Paneer Curry Combo', 'price': 120, 'category': 'Combos', 'is_veg': True, 'prep_time': 25, 'rating': 4.7},
            {'name': 'Chinese Combo - Veg Fried Rice with Manchurian', 'price': 120, 'category': 'Combos', 'is_veg': True, 'prep_time': 25, 'rating': 4.6},
            {'name': 'Non Veg Chinese Combo', 'price': 150, 'category': 'Combos', 'is_veg': False, 'prep_time': 25, 'rating': 4.7},
            {'name': 'Chicken Curry Combo', 'price': 120, 'category': 'Combos', 'is_veg': False, 'prep_time': 25, 'rating': 4.8},
            {'name': 'Egg Curry Combo', 'price': 100, 'category': 'Combos', 'is_veg': False, 'prep_time': 20, 'rating': 4.5},
            
            # NORTH INDIAN
            {'name': 'Poori Chole', 'price': 50, 'category': 'North Indian', 'is_veg': True, 'prep_time': 15, 'rating': 4.6},
            {'name': 'Chole Batura', 'price': 40, 'category': 'North Indian', 'is_veg': True, 'prep_time': 15, 'rating': 4.5},
            {'name': 'Dal Khichadi', 'price': 70, 'category': 'North Indian', 'is_veg': True, 'prep_time': 15, 'rating': 4.4},
            
            # PARATHAS
            {'name': 'Aloo Paratha with Curd (Small)', 'price': 10, 'category': 'Parathas', 'is_veg': True, 'prep_time': 12, 'rating': 4.5},
            {'name': 'Aloo Paratha with Curd (Large)', 'price': 15, 'category': 'Parathas', 'is_veg': True, 'prep_time': 15, 'rating': 4.6},
            {'name': 'Aloo Cheese Paratha with Curd (Small)', 'price': 10, 'category': 'Parathas', 'is_veg': True, 'prep_time': 12, 'rating': 4.6},
            {'name': 'Aloo Cheese Paratha with Curd (Large)', 'price': 15, 'category': 'Parathas', 'is_veg': True, 'prep_time': 15, 'rating': 4.7},
            {'name': 'Aloo Paneer Mix Paratha (Small)', 'price': 10, 'category': 'Parathas', 'is_veg': True, 'prep_time': 12, 'rating': 4.5},
            {'name': 'Aloo Paneer Mix Paratha (Large)', 'price': 15, 'category': 'Parathas', 'is_veg': True, 'prep_time': 15, 'rating': 4.6},
            {'name': 'Paneer Paratha with Curd (Small)', 'price': 10, 'category': 'Parathas', 'is_veg': True, 'prep_time': 12, 'rating': 4.6},
            {'name': 'Paneer Paratha with Curd (Large)', 'price': 15, 'category': 'Parathas', 'is_veg': True, 'prep_time': 15, 'rating': 4.7},
            {'name': 'Paneer Cheese Paratha with Curd (Large)', 'price': 15, 'category': 'Parathas', 'is_veg': True, 'prep_time': 15, 'rating': 4.7},
            {'name': 'Paneer Cheese Paratha with Curd (Extra Large)', 'price': 20, 'category': 'Parathas', 'is_veg': True, 'prep_time': 18, 'rating': 4.8},
            
            # PASTA
            {'name': 'Pasta Creamy Alfredo (White Sauce)', 'price': 70, 'category': 'Pasta', 'is_veg': True, 'prep_time': 20, 'rating': 4.5},
            {'name': 'Pasta Creamy Alfredo with Cheese (White Sauce)', 'price': 80, 'category': 'Pasta', 'is_veg': True, 'prep_time': 20, 'rating': 4.6},
            {'name': 'Peri Peri Mac N Cheese', 'price': 90, 'category': 'Pasta', 'is_veg': True, 'prep_time': 20, 'rating': 4.7},
            
            # ROLLS
            {'name': 'Veg Roll', 'price': 70, 'category': 'Rolls', 'is_veg': True, 'prep_time': 12, 'rating': 4.5},
            {'name': 'Veg Roll with Cheese', 'price': 80, 'category': 'Rolls', 'is_veg': True, 'prep_time': 12, 'rating': 4.6},
            {'name': 'Paneer Roll', 'price': 90, 'category': 'Rolls', 'is_veg': True, 'prep_time': 12, 'rating': 4.6},
            {'name': 'Paneer Roll with Cheese', 'price': 100, 'category': 'Rolls', 'is_veg': True, 'prep_time': 12, 'rating': 4.7},
            {'name': 'Egg Roll', 'price': 70, 'category': 'Rolls', 'is_veg': False, 'prep_time': 12, 'rating': 4.5},
            {'name': 'Egg Roll with Cheese', 'price': 80, 'category': 'Rolls', 'is_veg': False, 'prep_time': 12, 'rating': 4.6},
            {'name': 'Chicken Roll', 'price': 100, 'category': 'Rolls', 'is_veg': False, 'prep_time': 12, 'rating': 4.7},
            {'name': 'Chicken Roll with Cheese', 'price': 110, 'category': 'Rolls', 'is_veg': False, 'prep_time': 12, 'rating': 4.8},
            {'name': 'Peri Peri Chicken Roll', 'price': 100, 'category': 'Rolls', 'is_veg': False, 'prep_time': 12, 'rating': 4.7},
            {'name': 'Peri Peri Chicken Roll with Cheese', 'price': 110, 'category': 'Rolls', 'is_veg': False, 'prep_time': 12, 'rating': 4.8},
            {'name': 'BBQ Chicken Roll', 'price': 100, 'category': 'Rolls', 'is_veg': False, 'prep_time': 12, 'rating': 4.7},
            {'name': 'BBQ Chicken Roll with Cheese', 'price': 110, 'category': 'Rolls', 'is_veg': False, 'prep_time': 12, 'rating': 4.8},
            
            # BIRYANIS
            {'name': 'Veg Hyderabadi Biryani', 'price': 100, 'category': 'Biryanis', 'is_veg': True, 'prep_time': 30, 'rating': 4.7},
            {'name': 'Mushroom Donne Biryani', 'price': 120, 'category': 'Biryanis', 'is_veg': True, 'prep_time': 30, 'rating': 4.6},
            {'name': 'Egg Hyderabadi Biryani', 'price': 110, 'category': 'Biryanis', 'is_veg': False, 'prep_time': 30, 'rating': 4.6},
            {'name': 'Chicken Hyderabadi Biryani', 'price': 140, 'category': 'Biryanis', 'is_veg': False, 'prep_time': 30, 'rating': 4.8},
            {'name': 'Chicken Donne Biryani', 'price': 140, 'category': 'Biryanis', 'is_veg': False, 'prep_time': 30, 'rating': 4.8},
            {'name': 'Chicken Kabab Biryani', 'price': 150, 'category': 'Biryanis', 'is_veg': False, 'prep_time': 35, 'rating': 4.9},
            
            # BURGERS
            {'name': 'Veg Burger', 'price': 60, 'category': 'Burgers', 'is_veg': True, 'prep_time': 15, 'rating': 4.5},
            {'name': 'Veg Burger with Cheese', 'price': 70, 'category': 'Burgers', 'is_veg': True, 'prep_time': 15, 'rating': 4.6},
            {'name': 'Chicken Burger', 'price': 70, 'category': 'Burgers', 'is_veg': False, 'prep_time': 15, 'rating': 4.6},
            {'name': 'Chicken Burger with Cheese', 'price': 80, 'category': 'Burgers', 'is_veg': False, 'prep_time': 15, 'rating': 4.7},
            {'name': 'Peri Peri Chicken Burger', 'price': 90, 'category': 'Burgers', 'is_veg': False, 'prep_time': 15, 'rating': 4.7},
            {'name': 'Peri Peri Chicken Burger with Cheese', 'price': 100, 'category': 'Burgers', 'is_veg': False, 'prep_time': 15, 'rating': 4.8},
            {'name': 'BBQ Chicken Burger', 'price': 90, 'category': 'Burgers', 'is_veg': False, 'prep_time': 15, 'rating': 4.7},
            {'name': 'BBQ Chicken Burger with Cheese', 'price': 100, 'category': 'Burgers', 'is_veg': False, 'prep_time': 15, 'rating': 4.8},
            {'name': 'Vada Pav', 'price': 30, 'category': 'Burgers', 'is_veg': True, 'prep_time': 10, 'rating': 4.4},
            {'name': 'Vada Pav with Cheese', 'price': 40, 'category': 'Burgers', 'is_veg': True, 'prep_time': 10, 'rating': 4.5},
            {'name': 'Bun Samosa', 'price': 40, 'category': 'Burgers', 'is_veg': True, 'prep_time': 10, 'rating': 4.4},
            {'name': 'Bun Samosa with Cheese', 'price': 50, 'category': 'Burgers', 'is_veg': True, 'prep_time': 10, 'rating': 4.5},
            
            # MAGGI
            {'name': 'Maggi Masala', 'price': 35, 'category': 'Maggi', 'is_veg': True, 'prep_time': 10, 'rating': 4.4},
            {'name': 'Maggi - Peri Peri / Extra Masala / Corn / Cheese', 'price': 45, 'category': 'Maggi', 'is_veg': True, 'prep_time': 10, 'rating': 4.5},
            {'name': 'Maggi with Extra Masala/Peri Peri and Cheese', 'price': 50, 'category': 'Maggi', 'is_veg': True, 'prep_time': 10, 'rating': 4.6},
            
            # PIZZAS
            {'name': 'Chessy Garlic Bread', 'price': 50, 'category': 'Pizzas', 'is_veg': True, 'prep_time': 15, 'rating': 4.5},
            {'name': 'Margherita Pizza', 'price': 100, 'category': 'Pizzas', 'is_veg': True, 'prep_time': 20, 'rating': 4.6},
            {'name': 'Tandoori Paneer Pizza', 'price': 120, 'category': 'Pizzas', 'is_veg': True, 'prep_time': 20, 'rating': 4.7},
            {'name': 'Tandoori Mushroom Pizza', 'price': 120, 'category': 'Pizzas', 'is_veg': True, 'prep_time': 20, 'rating': 4.6},
            {'name': 'Bread Paneer Pizza', 'price': 50, 'category': 'Pizzas', 'is_veg': True, 'prep_time': 12, 'rating': 4.5},
            {'name': 'Bread Mushroom Pizza', 'price': 50, 'category': 'Pizzas', 'is_veg': True, 'prep_time': 12, 'rating': 4.5},
            
            # LASSI
            {'name': 'Buttermilk', 'price': 25, 'category': 'Lassi', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Sweet Lassi', 'price': 50, 'category': 'Lassi', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            {'name': 'Strawberry Lassi', 'price': 65, 'category': 'Lassi', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            {'name': 'Chocolate Lassi', 'price': 65, 'category': 'Lassi', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            {'name': 'Mango Lassi', 'price': 65, 'category': 'Lassi', 'is_veg': True, 'prep_time': 5, 'rating': 4.7},
            {'name': 'Banana Lassi', 'price': 65, 'category': 'Lassi', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Rose Lassi', 'price': 65, 'category': 'Lassi', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            
            # SODA
            {'name': 'Fresh Lime Soda', 'price': 35, 'category': 'Soda', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Masala Lemon Soda', 'price': 40, 'category': 'Soda', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Blue Lagoon', 'price': 50, 'category': 'Soda', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Mango Soda', 'price': 50, 'category': 'Soda', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Kala Khatta Soda', 'price': 50, 'category': 'Soda', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Fresh Fruit Bowl', 'price': 50, 'category': 'Soda', 'is_veg': True, 'prep_time': 10, 'rating': 4.6},
            {'name': 'Fruit Bowl with Ice cream', 'price': 65, 'category': 'Soda', 'is_veg': True, 'prep_time': 10, 'rating': 4.7},
            
            # MILK SHAKES
            {'name': 'Vanilla Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Chocolate Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            {'name': 'Butterscotch Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Black Currant Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Strawberry Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Kiwi Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Litchi Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Mango Milk Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            {'name': 'Banana Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Sapota Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Apple Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Muskmelon Milk Shake', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Cold Coffee', 'price': 50, 'category': 'Milk Shakes', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            
            # SPECIAL SHAKES
            {'name': 'Cold Coffee with Ice cream', 'price': 65, 'category': 'Special Shakes', 'is_veg': True, 'prep_time': 7, 'rating': 4.7},
            {'name': 'Oreo Shake', 'price': 65, 'category': 'Special Shakes', 'is_veg': True, 'prep_time': 7, 'rating': 4.7},
            {'name': 'Chocolate Brownie Shake', 'price': 65, 'category': 'Special Shakes', 'is_veg': True, 'prep_time': 7, 'rating': 4.7},
            {'name': 'KitKat Shake', 'price': 65, 'category': 'Special Shakes', 'is_veg': True, 'prep_time': 7, 'rating': 4.7},
            {'name': 'Butterfruit Milk Shake', 'price': 65, 'category': 'Special Shakes', 'is_veg': True, 'prep_time': 7, 'rating': 4.6},
            {'name': 'Rose Milk Shake', 'price': 65, 'category': 'Special Shakes', 'is_veg': True, 'prep_time': 7, 'rating': 4.6},
            
            # TEA & COFFEE
            {'name': 'Regular Tea', 'price': 15, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 3, 'rating': 4.3},
            {'name': 'Filter Coffee', 'price': 15, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 3, 'rating': 4.4},
            {'name': 'Fresh Lime Tea', 'price': 15, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 3, 'rating': 4.5},
            {'name': 'Black Tea', 'price': 15, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 3, 'rating': 4.3},
            {'name': 'Black Coffee', 'price': 15, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 3, 'rating': 4.4},
            {'name': 'Ginger Tea', 'price': 17, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 3, 'rating': 4.4},
            {'name': 'Ginger Coffee', 'price': 17, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 3, 'rating': 4.4},
            {'name': 'Hot Badam Milk', 'price': 17, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Café Mocha', 'price': 25, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            {'name': 'Horlicks', 'price': 25, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Hot Chocolate', 'price': 25, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 3, 'rating': 4.5},
            {'name': 'Boost', 'price': 25, 'category': 'Tea & Coffee', 'is_veg': True, 'prep_time': 3, 'rating': 4.3},
            
            # FRESH JUICES
            {'name': 'Lemon Juice', 'price': 25, 'category': 'Fresh Juices', 'is_veg': True, 'prep_time': 3, 'rating': 4.4},
            {'name': 'Watermelon Juice', 'price': 40, 'category': 'Fresh Juices', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Muskmelon Juice', 'price': 40, 'category': 'Fresh Juices', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Pineapple Juice', 'price': 40, 'category': 'Fresh Juices', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Orange Juice', 'price': 40, 'category': 'Fresh Juices', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            {'name': 'Mosambi Juice', 'price': 40, 'category': 'Fresh Juices', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Ganga Jamuna', 'price': 40, 'category': 'Fresh Juices', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Mix Fruit Juice', 'price': 50, 'category': 'Fresh Juices', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            
            # COLD DRINKS - COCA COLA
            {'name': 'Coke', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Sprite', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Fanta', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Thums Up', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Limca', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Maaza', 'price': 25, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Pepsi', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': '7up', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Mirinda', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Nimbooz', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Slice', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Mountain Dew', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Gatorade', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Power Up', 'price': 10, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.2},
            {'name': 'Gluco Energy', 'price': 10, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.2},
            {'name': 'Jeera Up Masala', 'price': 10, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Campa Lemon', 'price': 10, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.2},
            {'name': 'Campa Orange', 'price': 10, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.2},
            {'name': 'Campa Energy', 'price': 10, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.2},
            {'name': 'Campa Mango/Apple', 'price': 10, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.2},
            {'name': 'Mixfruit', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            {'name': 'Sports Drink', 'price': 10, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.2},
            {'name': 'Indian Mango', 'price': 20, 'category': 'Cold Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            
            # SMOOTH DRINKS
            {'name': 'Chocolate Milk', 'price': 20, 'category': 'Smooth Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Toffee Caramel', 'price': 20, 'category': 'Smooth Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Chocolate Hazelnut', 'price': 20, 'category': 'Smooth Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Coffee Frappe', 'price': 20, 'category': 'Smooth Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Lassi', 'price': 20, 'category': 'Smooth Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Frooti', 'price': 20, 'category': 'Smooth Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.3},
            {'name': 'Appy Fizz', 'price': 20, 'category': 'Smooth Drinks', 'is_veg': True, 'prep_time': 2, 'rating': 4.3},
            
            # TROPICANA
            {'name': 'Tropicana Orange', 'price': 20, 'category': 'Tropicana', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Tropicana Guava', 'price': 20, 'category': 'Tropicana', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Tropicana Mixed Fruit', 'price': 20, 'category': 'Tropicana', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Tropicana Mango', 'price': 20, 'category': 'Tropicana', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Tropicana Pomegranate', 'price': 20, 'category': 'Tropicana', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            
            # CHIA & OTHER
            {'name': 'Chia - Lemon', 'price': 15, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Chia - Blueberry', 'price': 15, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Chia - Orange', 'price': 15, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Chia - Litchi', 'price': 15, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Chia - Strawberry', 'price': 15, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Chia - Cream Bell', 'price': 15, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.4},
            {'name': 'Choco Milkshake', 'price': 35, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Butter scotch Milkshake', 'price': 35, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Coffee Milkshake', 'price': 30, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            {'name': 'Kesar Badam Milkshake', 'price': 30, 'category': 'Other Drinks', 'is_veg': True, 'prep_time': 5, 'rating': 4.5},
            
            # PAPER BOAT
            {'name': 'Paper Boat - Alphonso Mango', 'price': 25, 'category': 'Paper Boat', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Paper Boat - Lychee', 'price': 25, 'category': 'Paper Boat', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Paper Boat - Apple', 'price': 25, 'category': 'Paper Boat', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Paper Boat - Aamras', 'price': 25, 'category': 'Paper Boat', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Paper Boat - Orange', 'price': 25, 'category': 'Paper Boat', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Paper Boat - Coconut Water', 'price': 60, 'category': 'Paper Boat', 'is_veg': True, 'prep_time': 2, 'rating': 4.6},
            
            # ICE CREAM - DAIRY DAY
            {'name': 'Dairy Day - Alphonso Mango', 'price': 25, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Dairy Day - Chocolate Cone', 'price': 40, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Dairy Day - Triple Bar', 'price': 40, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.6},
            {'name': 'Dairy Day - Butterscotch Cone', 'price': 40, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Dairy Day - Black Currant Cone', 'price': 40, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Dairy Day - Strawberry Dolly', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Dairy Day - Mango Dolly', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Dairy Day - Chocobar', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Dairy Day - Ice Cream Sandwich', 'price': 30, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            
            # ICE CREAM - IDEAL
            {'name': 'Ideal - Triple Sundae Ice Cream', 'price': 60, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 5, 'rating': 4.7},
            {'name': 'Ideal - Kulfi Candy', 'price': 30, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Ideal - Vanilla Cone', 'price': 30, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Ideal - Matka Kulfi', 'price': 50, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.6},
            {'name': 'Ideal - Kaju Malai Cone', 'price': 50, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.6},
            {'name': 'Ideal - Kaju Malai Ice Cream', 'price': 50, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.6},
            {'name': 'Ideal - Chocolate Cone', 'price': 40, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Ideal - Chikku Almond', 'price': 50, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.6},
            {'name': 'Ideal - Maskmelon Ice Cream', 'price': 50, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Ideal - Mini Sundae Chocolate', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Ideal - Raspberry Dolly', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Ideal - Mango Dolly', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Ideal - Butterscotch Cone', 'price': 40, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.5},
            {'name': 'Ideal - Mammoth Ice Cream', 'price': 50, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 5, 'rating': 4.6},
            {'name': 'Ideal - Mini Sundae Strawberry', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Ideal - Mini Strawberry Cone', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Ideal - Chikku Cup Ice Cream', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Ideal - Mini Black Currant Cone', 'price': 20, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.4},
            {'name': 'Ideal - Cassata Ice Cream', 'price': 50, 'category': 'Ice Cream', 'is_veg': True, 'prep_time': 2, 'rating': 4.6},
        ]
        
        # Add foods to database
        for idx, food_data in enumerate(foods_data):
            food = Food(
                id=f'food-{str(idx+1).zfill(3)}',
                available=True,
                review_count=int(food_data.get('rating', 4.5) * 10),
                **food_data
            )
            db.session.add(food)
        db.session.commit()

@app.route('/', methods=['GET'])
def root():
    return {
        'message': 'Campus Runner Backend API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth/*',
            'menu': '/api/menu/*',
            'cart': '/api/cart/*',
            'orders': '/api/order/*',
            'runners': '/api/runner/*',
            'admin': '/api/admin/*'
        }
    }, 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'Backend is running'}, 200

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email endpoint to verify email configuration"""
    try:
        recipient = request.json.get('email', 'test@example.com') if request.is_json else 'test@example.com'
        
        print(f"\n📧 Testing email to: {recipient}")
        print(f"📧 Mail Server: {app.config.get('MAIL_SERVER')}")
        print(f"📧 Mail Username: {app.config.get('MAIL_USERNAME')}")
        
        html = f"""
        <html>
            <body style="font-family: Arial">
                <h2 style="color: #ff8c00;">🎉 Email System Working!</h2>
                <p>This is a test email from Campus Runner.</p>
                <p>Your email configuration is set up correctly.</p>
                <hr>
                <p><strong>Server:</strong> {app.config.get('MAIL_SERVER')}</p>
                <p><strong>Port:</strong> {app.config.get('MAIL_PORT')}</p>
            </body>
        </html>
        """
        
        from utils import send_email_in_background
        send_email_in_background(app, "Campus Runner - Test Email", [recipient], html)
        
        return jsonify({
            'success': True,
            'message': f'Test email queued to {recipient}',
            'config': {
                'mail_server': app.config.get('MAIL_SERVER'),
                'mail_port': app.config.get('MAIL_PORT'),
                'mail_username': app.config.get('MAIL_USERNAME'),
                'mail_tls': app.config.get('MAIL_USE_TLS')
            }
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
