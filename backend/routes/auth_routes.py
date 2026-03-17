from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, RewardPoints
import uuid
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({'error': 'Missing required fields: name, email, password'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'User already exists with this email'}), 409
        
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            role=data.get('role', 'customer'),
            is_verified=True
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create reward points for the user
        reward = RewardPoints(
            id=str(uuid.uuid4()),
            user_id=user.id,
            total_points=0,
            points_balance=0,
            tier='bronze'
        )
        db.session.add(reward)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=30))
        
        print(f"✅ User registered: {data['email']}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
    
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            print(f"⚠️ Failed login attempt for: {data['email']}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=30))
        
        print(f"✅ User logged in: {data['email']}")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
    
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'profile_image' in data:
            user.profile_image = data['profile_image']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout a user"""
    return jsonify({'message': 'Logout successful'}), 200
