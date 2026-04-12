from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import os
import sys
from sqlalchemy import inspect, text

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
# Optional backend/.env: fills in vars missing from project root (e.g. MAIL_* only in backend/)
backend_dotenv = os.path.join(backend_dir, '.env')
if os.path.exists(backend_dotenv):
    load_dotenv(backend_dotenv, override=False)

# Create Flask app
app = Flask(__name__)


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in ('1', 'true', 'yes', 'on')


# Configuration
database_url = os.getenv('DATABASE_URL', 'sqlite:///campusrunner.db')
if database_url.startswith('sqlite:///') and not database_url.startswith('sqlite:////'):
    database_name = database_url.replace('sqlite:///', '', 1)
    database_path = os.path.join(parent_dir, 'instance', database_name)
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    database_url = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

# Email Configuration (MAIL_* is canonical; EMAIL_ADDRESS / EMAIL_PASSWORD match backend/.env.example)
_mail_user = (os.getenv('MAIL_USERNAME') or os.getenv('EMAIL_ADDRESS', '')).strip()
# Gmail app passwords are often pasted with spaces; SMTP expects 16 chars without spaces
_mail_pass = (os.getenv('MAIL_PASSWORD') or os.getenv('EMAIL_PASSWORD', '')).replace(' ', '').strip()
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = _env_bool('MAIL_USE_TLS', True)
app.config['MAIL_USE_SSL'] = _env_bool('MAIL_USE_SSL', False)
app.config['MAIL_DEBUG'] = _env_bool('MAIL_DEBUG', False)
app.config['MAIL_TIMEOUT'] = int(os.getenv('MAIL_TIMEOUT', 30))
app.config['MAIL_USERNAME'] = _mail_user
app.config['MAIL_PASSWORD'] = _mail_pass
_default_sender = (os.getenv('MAIL_DEFAULT_SENDER', '') or _mail_user or 'noreply@campusrunner.com').strip()
app.config['MAIL_DEFAULT_SENDER'] = _default_sender
# Never suppress sends in normal dev unless explicitly set (Flask-Mail defaults suppress to app.testing only)
if 'MAIL_SUPPRESS_SEND' in os.environ:
    app.config['MAIL_SUPPRESS_SEND'] = _env_bool('MAIL_SUPPRESS_SEND', False)

# Initialize extensions
from models import db
db.init_app(app)

# Improved CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173", 
            "http://localhost:5174",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:3000",
            "http://10.17.20.172:5173",
            "http://10.17.20.172:5174",
            "http://10.17.20.172:3000"
        ],
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

jwt = JWTManager(app)

try:
    from flask_socketio import SocketIO, join_room
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    from socketio_events import register_socketio_events

    @socketio.on('join_user_room')
    def join_user_room(data):
        user_id = data.get('user_id') if isinstance(data, dict) else None
        if user_id:
            join_room(f'user:{user_id}')

    @socketio.on('join_runner_room')
    def join_runner_room():
        join_room('runners')

    @socketio.on('join_staff_room')
    def join_staff_room():
        join_room('staff')

    register_socketio_events(socketio)

    print("✅ Socket.IO initialized successfully")
except Exception as socket_error:
    print(f"⚠️ Socket.IO unavailable: {str(socket_error)}")
    socketio = None

# Handle CORS preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'success': True})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,PATCH,POST,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

# Initialize Flask-Mail
try:
    mail = Mail()
    mail.init_app(app)
    print("✅ Mail service initialized successfully")
except Exception as mail_error:
    print(f"⚠️ Mail initialization warning: {str(mail_error)}")
    mail = Mail()

# Print email configuration for debugging
try:
    with app.app_context():
        print(f"\n=== EMAIL CONFIGURATION ===")
        print(f"Mail Server: {app.config.get('MAIL_SERVER')}")
        print(f"Mail Port: {app.config.get('MAIL_PORT')}")
        print(f"Mail Username: {app.config.get('MAIL_USERNAME')}")
        print(f"Mail TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"Mail Has Password: {'Yes' if app.config.get('MAIL_PASSWORD') else 'No'}")
        print(f"===========================\n")
except Exception as config_error:
    print(f"⚠️ Error printing config: {str(config_error)}")

# Register blueprints (routes)
from routes.auth_routes import auth_bp
from routes.menu_routes import menu_bp
from routes.order_routes import order_bp
from routes.runner_routes import runner_bp
from routes.staff_admin_routes import staff_admin_bp
from routes.cart_routes import cart_bp
from routes.checkout_routes import checkout_bp
from routes.rewards_routes import rewards_bp
from routes.payment_routes import payment_bp
from routes.payment_methods_routes import payment_methods_bp
from routes.notification_routes import notification_bp
from routes.review_routes import review_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(menu_bp, url_prefix='/api/menu')
app.register_blueprint(order_bp, url_prefix='/api/order')
app.register_blueprint(order_bp, url_prefix='/api/orders', name='orders_alias')
app.register_blueprint(checkout_bp, url_prefix='/api/checkout')
app.register_blueprint(runner_bp, url_prefix='/api/runner')
app.register_blueprint(rewards_bp, url_prefix='/api/rewards')
app.register_blueprint(staff_admin_bp, url_prefix='/api/admin')
app.register_blueprint(cart_bp, url_prefix='/api/cart')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(payment_methods_bp, url_prefix='/api/payment-methods')
app.register_blueprint(notification_bp, url_prefix='/api/notifications')
app.register_blueprint(review_bp, url_prefix='/api/reviews')

# Global error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    import traceback
    print(f"🔴 Unhandled exception: {str(error)}")
    print(f"📍 Traceback: {traceback.format_exc()}")
    return jsonify({
        'error': 'An error occurred',
        'message': str(error),
        'type': type(error).__name__
    }), 500

# Create tables and initialize data
def run_startup_migrations():
    """Apply lightweight SQLite schema fixes for existing local databases."""
    try:
        inspector = inspect(db.engine)

        if 'orders' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('orders')}
            required_order_columns = {
                'received_by_canteen_at': 'ALTER TABLE orders ADD COLUMN received_by_canteen_at DATETIME',
                'preparation_started_at': 'ALTER TABLE orders ADD COLUMN preparation_started_at DATETIME',
                'ready_for_pickup_at': 'ALTER TABLE orders ADD COLUMN ready_for_pickup_at DATETIME',
                'picked_up_at': 'ALTER TABLE orders ADD COLUMN picked_up_at DATETIME',
                'in_transit_at': 'ALTER TABLE orders ADD COLUMN in_transit_at DATETIME',
                'delivered_at': 'ALTER TABLE orders ADD COLUMN delivered_at DATETIME',
            }

            for column_name, sql in required_order_columns.items():
                if column_name not in existing_columns:
                    db.session.execute(text(sql))
                    print(f"✅ Added missing orders.{column_name} column")

            db.session.commit()

        if 'foods' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('foods')}
            required_food_columns = {
                'calories': 'ALTER TABLE foods ADD COLUMN calories INTEGER',
                'ingredients': 'ALTER TABLE foods ADD COLUMN ingredients TEXT',
                'counter_number': 'ALTER TABLE foods ADD COLUMN counter_number INTEGER',
                'counter_name': 'ALTER TABLE foods ADD COLUMN counter_name VARCHAR(255)',
            }

            for column_name, sql in required_food_columns.items():
                if column_name not in existing_columns:
                    db.session.execute(text(sql))
                    print(f"✅ Added missing foods.{column_name} column")

            db.session.commit()

        if 'cart_items' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('cart_items')}
            if 'customizations' not in existing_columns:
                db.session.execute(text('ALTER TABLE cart_items ADD COLUMN customizations TEXT'))
                print('✅ Added missing cart_items.customizations column')
                db.session.commit()

        if 'order_items' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('order_items')}
            if 'customizations' not in existing_columns:
                db.session.execute(text('ALTER TABLE order_items ADD COLUMN customizations TEXT'))
                print('✅ Added missing order_items.customizations column')
                db.session.commit()

        if 'deliveries' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('deliveries')}
            required_delivery_columns = {
                'accepted_at': 'ALTER TABLE deliveries ADD COLUMN accepted_at DATETIME',
                'picked_at': 'ALTER TABLE deliveries ADD COLUMN picked_at DATETIME',
                'on_the_way_at': 'ALTER TABLE deliveries ADD COLUMN on_the_way_at DATETIME',
                'delivered_at': 'ALTER TABLE deliveries ADD COLUMN delivered_at DATETIME',
            }

            for column_name, sql in required_delivery_columns.items():
                if column_name not in existing_columns:
                    db.session.execute(text(sql))
                    print(f"✅ Added missing deliveries.{column_name} column")
            db.session.commit()

        if 'payments' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('payments')}
            required_payment_columns = {
                'user_id': 'ALTER TABLE payments ADD COLUMN user_id VARCHAR(36)',
                'method': "ALTER TABLE payments ADD COLUMN method VARCHAR(20) DEFAULT 'upi'",
                'upi_id': 'ALTER TABLE payments ADD COLUMN upi_id VARCHAR(120)',
                'card_last4': 'ALTER TABLE payments ADD COLUMN card_last4 VARCHAR(4)',
                'card_number_hash': 'ALTER TABLE payments ADD COLUMN card_number_hash VARCHAR(255)',
                'card_holder_name': 'ALTER TABLE payments ADD COLUMN card_holder_name VARCHAR(120)',
                'card_expiry': 'ALTER TABLE payments ADD COLUMN card_expiry VARCHAR(7)',
                'updated_at': 'ALTER TABLE payments ADD COLUMN updated_at DATETIME',
            }

            for column_name, sql in required_payment_columns.items():
                if column_name not in existing_columns:
                    db.session.execute(text(sql))
                    print(f"✅ Added missing payments.{column_name} column")

            db.session.commit()

        if 'notifications' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('notifications')}
            required_notification_columns = {
                'related_id': 'ALTER TABLE notifications ADD COLUMN related_id VARCHAR(36)',
                'action_url': 'ALTER TABLE notifications ADD COLUMN action_url VARCHAR(255)',
            }

            for column_name, sql in required_notification_columns.items():
                if column_name not in existing_columns:
                    db.session.execute(text(sql))
                    print(f"✅ Added missing notifications.{column_name} column")

            db.session.commit()

        if 'reviews' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('reviews')}
            if 'order_id' not in existing_columns:
                db.session.execute(text('ALTER TABLE reviews ADD COLUMN order_id VARCHAR(36)'))
                print('✅ Added missing reviews.order_id column')
            if 'is_seeded' not in existing_columns:
                db.session.execute(text('ALTER TABLE reviews ADD COLUMN is_seeded BOOLEAN DEFAULT 0'))
                print('✅ Added missing reviews.is_seeded column')
            if 'seeded_name' not in existing_columns:
                db.session.execute(text('ALTER TABLE reviews ADD COLUMN seeded_name VARCHAR(255)'))
                print('✅ Added missing reviews.seeded_name column')
            db.session.commit()

        if 'order_otps' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('order_otps')}
            if 'otp_type' not in existing_columns:
                db.session.execute(text("ALTER TABLE order_otps ADD COLUMN otp_type VARCHAR(20) DEFAULT 'delivery'"))
                print('✅ Added missing order_otps.otp_type column')
                db.session.commit()

        if 'users' in inspector.get_table_names():
            existing_columns = {column['name'] for column in inspector.get_columns('users')}
            if 'notification_preferences' not in existing_columns:
                db.session.execute(text("ALTER TABLE users ADD COLUMN notification_preferences JSON"))
                print('✅ Added missing users.notification_preferences column')
                db.session.commit()
    except Exception as migration_error:
        db.session.rollback()
        print(f"⚠️ Startup migration warning: {migration_error}")


try:
    with app.app_context():
        db.create_all()
        run_startup_migrations()
        print("✅ Database tables created")
        try:
            from seed import seed_sample_reviews
            seed_sample_reviews()
        except Exception as seed_error:
            print(f"⚠️ Review seed warning: {seed_error}")
        
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
            print("✓ Food items added to database")
        
        # Create default admin user if doesn't exist
        try:
            from models import User
            import uuid
            admin_email = 'admin@rvu.edu.in'
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if not existing_admin:
                admin_user = User(
                    id=str(uuid.uuid4()),
                    name='Admin',
                    email=admin_email,
                    phone='9876543210',
                    role='admin',
                    is_verified=True
                )
                admin_user.set_password('admin@123')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created")
                print(f"   📧 Email: {admin_email}")
                print(f"   🔑 Password: admin@123")
            else:
                print("✅ Admin user already exists")
        except Exception as admin_error:
            print(f"⚠️ Admin creation error: {str(admin_error)}")
            db.session.rollback()
            
        print("✅ Database initialization complete!")
        
except Exception as init_error:
    print(f"❌ Database initialization failed: {str(init_error)}")
    import traceback
    print(f"📍 Traceback: {traceback.format_exc()}")

@app.route('/', methods=['GET'])
def root():
    return {
        'message': 'Campus Runner Backend API',
        'version': '1.0.0',
        'status': 'running ✅',
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
        
        from utils import send_otp_email_sync
        sent, error = send_otp_email_sync(
            app,
            "Campus Runner - Test Email",
            [recipient],
            html,
            otp_for_log=None,
        )
        return jsonify({
            'success': sent,
            'message': (f"Test email sent to {recipient}" if sent else f"Test email could not be sent to {recipient}"),
            'error': error,
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
    if socketio:
        socketio.run(app, debug=True, port=5000)
    else:
        app.run(debug=True, port=5000)
