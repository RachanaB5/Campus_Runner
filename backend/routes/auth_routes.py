from flask import Blueprint, request, jsonify, has_request_context, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, RewardPoints, Order, Runner
import uuid
from datetime import datetime, timedelta
import random
import re
import os

auth_bp = Blueprint('auth', __name__)
otp_store = {}

OTP_RESEND_COOLDOWN_SECONDS = 60


def normalize_email(value):
    if value is None:
        return ''
    return str(value).strip().lower()


def generate_otp():
    return ''.join(random.choices('0123456789', k=6))


def _dev_mode_expose_otp():
    try:
        if has_request_context() and getattr(current_app, 'debug', False):
            return True
    except RuntimeError:
        pass
    return (
        os.environ.get('FLASK_ENV', '').lower() == 'development'
        or os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    )


def dispatch_otp_email(to_email, otp, purpose):
    """Send OTP synchronously so SMTP errors are visible. Returns (sent, error_or_none)."""
    from app import app
    from utils import send_otp_email_sync

    subject = f'CampusRunner {purpose} OTP'
    html = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color:#F97316;">CampusRunner Verification</h2>
            <p>Your {purpose.lower()} OTP is:</p>
            <h1 style="letter-spacing:6px;color:#EA580C;">{otp}</h1>
            <p>This code expires in 10 minutes.</p>
          </body>
        </html>
        """
    return send_otp_email_sync(app, subject, [to_email], html, otp_for_log=otp)

@auth_bp.route('/register', methods=['POST'])
@auth_bp.route('/signup', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({'error': 'Missing required fields: name, email, password'}), 400
        email = data['email'].strip().lower()
        
        # Let an unverified account finish signup instead of getting stuck.
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.is_verified:
                return jsonify({'error': 'User already exists with this email'}), 409

            existing_user.name = data['name']
            existing_user.phone = data.get('phone')
            existing_user.role = data.get('role', existing_user.role or 'customer')
            existing_user.set_password(data['password'])
            user = existing_user
            db.session.commit()
        else:
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                name=data['name'],
                email=email,
                phone=data.get('phone'),
                role=data.get('role', 'customer'),
                is_verified=False
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
        
        # Create reward points for the user if needed
        reward = RewardPoints.query.filter_by(user_id=user.id).first()
        if not reward:
            reward = RewardPoints(
                id=str(uuid.uuid4()),
                user_id=user.id,
                total_points=0,
                points_balance=0,
                tier='bronze'
            )
            db.session.add(reward)
            db.session.commit()
        
        print(f"✅ User registered: {data['email']}")
        now = datetime.utcnow()
        otp = generate_otp()
        otp_store[user.email] = {
            'otp': otp,
            'purpose': 'signup',
            'expires_at': now + timedelta(minutes=10),
            'last_sent_at': now,
        }
        sent, _mail_err = dispatch_otp_email(user.email, otp, 'Signup Verification')

        body = {
            'message': 'User registered successfully. Check your email for the verification code.'
            if sent else 'User registered successfully. Email could not be sent — configure SMTP or check the server log for this OTP.',
            'user': user.to_dict(),
            'requires_verification': True,
            'email_sent': sent,
        }
        # Automated E2E only: set E2E_AUTH_OTP_IN_RESPONSE=1 on the API process; never in production.
        if os.environ.get('E2E_AUTH_OTP_IN_RESPONSE') == '1':
            body['otp'] = otp
        if not sent and _dev_mode_expose_otp():
            body['dev_otp'] = otp
        return jsonify(body), 201
    
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify signup OTP and issue a session. Password reset uses /reset-password only."""
    try:
        data = request.get_json() or {}
        email = normalize_email(data.get('email'))
        otp = (data.get('otp') or '').strip()
        record = otp_store.get(email)
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400
        if not record or record['otp'] != otp:
            return jsonify({'error': 'Invalid OTP'}), 400
        if datetime.utcnow() > record['expires_at']:
            return jsonify({'error': 'OTP expired'}), 400
        if record.get('purpose') != 'signup':
            return jsonify({'error': 'Use the password reset form for this code'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user.is_verified = True
        db.session.commit()
        otp_store.pop(email, None)
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=30))
        
        return jsonify({
            'message': 'Email verified successfully',
            'user': user.to_dict(),
            'access_token': access_token,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend signup or password-reset OTP with cooldown."""
    data = request.get_json() or {}
    email = normalize_email(data.get('email'))
    purpose = (data.get('purpose') or 'signup').strip().lower()
    if purpose not in ('signup', 'password_reset'):
        return jsonify({'error': 'Invalid purpose'}), 400
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    now = datetime.utcnow()

    if purpose == 'signup':
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user.is_verified:
            return jsonify({'error': 'Email is already verified'}), 400
    else:
        if not user:
            return jsonify({'error': 'User not found'}), 404

    existing = otp_store.get(email)
    if existing and existing.get('last_sent_at'):
        elapsed = (now - existing['last_sent_at']).total_seconds()
        if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
            wait = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            return jsonify({
                'error': f'Please wait {wait}s before requesting another code',
                'code': 'COOLDOWN',
                'retry_after': wait,
            }), 429

    otp = generate_otp()
    otp_store[email] = {
        'otp': otp,
        'purpose': purpose,
        'expires_at': now + timedelta(minutes=10),
        'last_sent_at': now,
    }
    label = 'Signup Verification' if purpose == 'signup' else 'Password Reset'
    sent, _ = dispatch_otp_email(email, otp, label)
    payload = {'message': 'OTP sent' if sent else 'OTP generated but email was not sent', 'email_sent': sent}
    if not sent and _dev_mode_expose_otp():
        payload['dev_otp'] = otp
    return jsonify(payload), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset OTP."""
    data = request.get_json() or {}
    email = normalize_email(data.get('email'))
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    now = datetime.utcnow()
    existing = otp_store.get(email)
    if existing and existing.get('last_sent_at'):
        elapsed = (now - existing['last_sent_at']).total_seconds()
        if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
            wait = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            return jsonify({
                'error': f'Please wait {wait}s before requesting another code',
                'code': 'COOLDOWN',
                'retry_after': wait,
            }), 429

    otp = generate_otp()
    otp_store[email] = {
        'otp': otp,
        'purpose': 'password_reset',
        'expires_at': now + timedelta(minutes=10),
        'last_sent_at': now,
    }
    sent, _ = dispatch_otp_email(email, otp, 'Password Reset')
    payload = {
        'message': 'Password reset OTP sent' if sent else 'Password reset code generated but email was not sent.',
        'email_sent': sent,
    }
    if not sent and _dev_mode_expose_otp():
        payload['dev_otp'] = otp
    return jsonify(payload), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using OTP."""
    try:
        data = request.get_json() or {}
        email = normalize_email(data.get('email'))
        otp = (data.get('otp') or '').strip()
        password = data.get('password')
        record = otp_store.get(email)
        
        if not email or not otp or not password:
            return jsonify({'error': 'Email, OTP, and password are required'}), 400
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        if not record or record['otp'] != otp or record.get('purpose') != 'password_reset':
            return jsonify({'error': 'Invalid OTP'}), 400
        if datetime.utcnow() > record['expires_at']:
            return jsonify({'error': 'OTP expired'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user.set_password(password)
        otp_store.pop(email, None)
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        email = data['email'].strip().lower()
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(data['password']):
            print(f"⚠️ Failed login attempt for: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401

        if not user.is_verified:
            return jsonify({
                'error': 'Please verify your RV University email before logging in. Check your inbox for the code.',
                'code': 'EMAIL_NOT_VERIFIED',
            }), 403
        
        # Create access token
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=30))
        
        print(f"✅ User logged in: {email}")
        
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

        reward = RewardPoints.query.filter_by(user_id=user_id).first()
        runner = Runner.query.filter_by(user_id=user_id).first()
        total_orders = Order.query.filter_by(customer_id=user_id, status='delivered').count()
        profile = user.to_dict()
        profile.update({
            'member_since': user.created_at.strftime('%B %Y') if user.created_at else None,
            'stats': {
                'total_orders': total_orders,
                'total_points': reward.points_balance if reward else 0,
                'lifetime_points': reward.total_points if reward else 0,
                'deliveries_made': runner.total_deliveries if runner else 0,
            }
        })
        return jsonify(profile), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/update-profile', methods=['PUT', 'OPTIONS'])
@auth_bp.route('/profile', methods=['PUT', 'OPTIONS'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        changed = False
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if name and len(name) < 2:
                return jsonify({'error': 'Name must be at least 2 characters'}), 400
            if name:
                user.name = name
                changed = True
        if 'phone' in data:
            phone = re.sub(r'\D', '', str(data.get('phone') or ''))
            if phone and not re.match(r'^\d{10}$', phone):
                return jsonify({'error': 'Enter a valid 10-digit phone number'}), 400
            user.phone = phone
            changed = True
        if 'profile_image' in data:
            user.profile_image = data['profile_image']
            changed = True
        if 'avatar_url' in data:
            user.profile_image = data['avatar_url']
            changed = True

        if changed:
            db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json() or {}
        current_password = data.get('current_password') or ''
        new_password = data.get('new_password') or ''
        confirm_password = data.get('confirm_password') or ''

        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        if new_password != confirm_password:
            return jsonify({'error': 'New passwords do not match'}), 400
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        if current_password == new_password:
            return jsonify({'error': 'New password must be different from current password'}), 400

        user.set_password(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/notification-preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json() or {}
        allowed_keys = {'order_updates', 'runner_assigned', 'order_delivered', 'new_orders_available', 'reward_points', 'promotions'}
        current_prefs = user.notification_preferences or {}
        next_prefs = {**current_prefs}
        for key, value in data.items():
            if key in allowed_keys:
                next_prefs[key] = bool(value)
        user.notification_preferences = next_prefs
        db.session.commit()
        return jsonify({'success': True, 'preferences': user.notification_preferences}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout a user"""
    return jsonify({'message': 'Logout successful'}), 200
