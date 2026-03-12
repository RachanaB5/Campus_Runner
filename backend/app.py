from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

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
mail = Mail(app)

# Register blueprints (routes)
from routes.auth_routes import auth_bp
from routes.menu_routes import menu_bp
from routes.order_routes import order_bp
from routes.runner_routes import runner_bp
from routes.staff_admin_routes import staff_admin_bp
from routes.cart_routes import cart_bp
from routes.checkout_routes import checkout_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(menu_bp, url_prefix='/api/menu')
app.register_blueprint(order_bp, url_prefix='/api/order')
app.register_blueprint(checkout_bp, url_prefix='/api/checkout')
app.register_blueprint(runner_bp, url_prefix='/api/runner')
app.register_blueprint(staff_admin_bp, url_prefix='/api/admin')
app.register_blueprint(cart_bp, url_prefix='/api/cart')

# Create tables
with app.app_context():
    db.create_all()
    # Auto-initialize database on app startup if empty
    from models import Food
    if Food.query.count() == 0:
        # Fixed food IDs for consistency across restarts
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
        foods_data = [
            {'id': FOOD_IDS['butter_chicken'], 'name': 'Butter Chicken', 'description': 'Tender chicken in creamy tomato-based sauce with butter', 'price': 240.00, 'category': 'Main Course', 'prep_time': 25, 'rating': 4.8},
            {'id': FOOD_IDS['chicken_biryani'], 'name': 'Chicken Biryani', 'description': 'Aromatic basmati rice with tender chicken pieces and spices', 'price': 200.00, 'category': 'Main Course', 'prep_time': 30, 'rating': 4.7},
            {'id': FOOD_IDS['paneer_tikka'], 'name': 'Paneer Tikka Masala', 'description': 'Cottage cheese cooked in aromatic tomato and cream sauce', 'price': 220.00, 'category': 'Main Course', 'prep_time': 25, 'rating': 4.6},
            {'id': FOOD_IDS['veg_fried_rice'], 'name': 'Veg Fried Rice', 'description': 'Fragrant basmati rice stir-fried with fresh vegetables and soy sauce', 'price': 140.00, 'category': 'Rice', 'prep_time': 15, 'rating': 4.5},
            {'id': FOOD_IDS['chicken_fried_rice'], 'name': 'Chicken Fried Rice', 'description': 'Basmati rice with tender chicken pieces and stir-fried vegetables', 'price': 180.00, 'category': 'Rice', 'prep_time': 18, 'rating': 4.6},
            {'id': FOOD_IDS['dal_makhani'], 'name': 'Dal Makhani', 'description': 'Slow-cooked black lentils with cream and aromatic spices', 'price': 130.00, 'category': 'Vegetarian', 'prep_time': 20, 'rating': 4.5},
            {'id': FOOD_IDS['aloo_gobi'], 'name': 'Aloo Gobi', 'description': 'Potatoes and cauliflower cooked with fresh ginger and spices', 'price': 110.00, 'category': 'Vegetarian', 'prep_time': 18, 'rating': 4.4},
            {'id': FOOD_IDS['samosa'], 'name': 'Samosa (4 pcs)', 'description': 'Crispy fried pastry filled with spiced potatoes and peas', 'price': 50.00, 'category': 'Appetizers', 'prep_time': 10, 'rating': 4.3},
            {'id': FOOD_IDS['garlic_naan'], 'name': 'Garlic Naan', 'description': 'Soft Indian flatbread baked in tandoor with garlic and butter', 'price': 60.00, 'category': 'Bread', 'prep_time': 8, 'rating': 4.7},
            {'id': FOOD_IDS['roti'], 'name': 'Roti', 'description': 'Traditional Indian wheat flatbread', 'price': 30.00, 'category': 'Bread', 'prep_time': 5, 'rating': 4.5},
            {'id': FOOD_IDS['coke'], 'name': 'Coke (250ml)', 'description': 'Cold carbonated beverage', 'price': 30.00, 'category': 'Beverages', 'prep_time': 2, 'rating': 4.4},
            {'id': FOOD_IDS['mango_lassi'], 'name': 'Mango Lassi', 'description': 'Traditional yogurt-based mango drink', 'price': 80.00, 'category': 'Beverages', 'prep_time': 5, 'rating': 4.6},
            {'id': FOOD_IDS['gulab_jamun'], 'name': 'Gulab Jamun (4 pcs)', 'description': 'Soft spongy balls in sugar syrup', 'price': 70.00, 'category': 'Desserts', 'prep_time': 5, 'rating': 4.7},
            {'id': FOOD_IDS['ice_cream'], 'name': 'Ice Cream (Vanilla/Chocolate)', 'description': 'Creamy cold dessert', 'price': 50.00, 'category': 'Desserts', 'prep_time': 2, 'rating': 4.5},
        ]
        for food_data in foods_data:
            food = Food(**food_data, available=True, review_count=int(food_data['rating'] * 10))
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
