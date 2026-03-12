from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Checkout, Order, OrderItem, User, Food, Delivery
from datetime import datetime, timedelta
from utils import send_order_confirmation_email
import uuid
import re

checkout_bp = Blueprint('checkout', __name__)

def generate_order_number():
    """Generate unique order number"""
    date = datetime.utcnow().strftime('%Y%m%d')
    random_part = str(uuid.uuid4()).split('-')[0][:4].upper()
    return f'ORD-{date}-{random_part}'

@checkout_bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_checkout():
    """Validate checkout information before placing order"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Create or update checkout record
        checkout = Checkout(
            id=str(uuid.uuid4()),
            customer_id=user_id,
            delivery_address=data.get('delivery_address', ''),
            delivery_city=data.get('delivery_city', ''),
            delivery_pincode=data.get('delivery_pincode', ''),
            customer_phone=data.get('customer_phone', ''),
            special_instructions=data.get('special_instructions', ''),
            payment_method=data.get('payment_method', ''),
            subtotal=float(data.get('subtotal', 0)),
            tax_amount=float(data.get('tax_amount', 0)),
            delivery_fee=float(data.get('delivery_fee', 0)),
            final_total=float(data.get('final_total', 0)),
            discount_amount=float(data.get('discount_amount', 0))
        )
        
        # Validate all fields
        if not checkout.validate_address():
            return jsonify({
                'success': False,
                'errors': {
                    'address': 'Please enter a valid delivery address (min 10 characters)',
                    'city': 'Please enter a valid city name',
                    'pincode': 'Please enter a valid pincode (5-6 digits)'
                },
                'validation_status': checkout.to_dict()
            }), 400
        
        if not checkout.validate_phone():
            return jsonify({
                'success': False,
                'errors': {
                    'phone': 'Please enter a valid phone number (10+ digits)'
                },
                'validation_status': checkout.to_dict()
            }), 400
        
        if not checkout.payment_method:
            return jsonify({
                'success': False,
                'errors': {
                    'payment_method': 'Please select a payment method'
                },
                'validation_status': checkout.to_dict()
            }), 400
        
        # All validations passed
        checkout.is_address_valid = True
        checkout.is_phone_valid = True
        checkout.is_payment_method_selected = True
        checkout.is_items_available = True
        
        return jsonify({
            'success': True,
            'message': 'All checkout information is valid',
            'validation_status': checkout.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@checkout_bp.route('/confirm', methods=['POST'])
@jwt_required()
def confirm_checkout():
    """Confirm checkout and create order"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'Order must contain items'}), 400
        
        # Validate checkout information first
        checkout_data = {
            'delivery_address': data.get('delivery_address'),
            'delivery_city': data.get('delivery_city'),
            'delivery_pincode': data.get('delivery_pincode'),
            'customer_phone': data.get('customer_phone'),
            'payment_method': data.get('payment_method')
        }
        
        checkout = Checkout(
            id=str(uuid.uuid4()),
            customer_id=user_id,
            delivery_address=checkout_data['delivery_address'],
            delivery_city=checkout_data['delivery_city'],
            delivery_pincode=checkout_data['delivery_pincode'],
            customer_phone=checkout_data['customer_phone'],
            payment_method=checkout_data['payment_method'],
            subtotal=float(data.get('subtotal', 0)),
            tax_amount=float(data.get('tax_amount', 0)),
            delivery_fee=float(data.get('delivery_fee', 0)),
            final_total=float(data.get('final_total', 0)),
            special_instructions=data.get('delivery_instructions') or data.get('special_instructions', ''),
            discount_amount=float(data.get('discount_amount', 0))
        )
        
        # Validate all information
        checkout.is_items_available = bool(items) and len(items) > 0
        
        if not checkout.validate_all():
            checkout.validate_address()
            checkout.validate_phone()
            checkout.is_payment_method_selected = bool(checkout.payment_method)
            
            # Debug logging
            print(f"\n=== CHECKOUT VALIDATION FAILED ===")
            print(f"Address valid: {checkout.is_address_valid} (address='{checkout.delivery_address}', city='{checkout.delivery_city}', pincode='{checkout.delivery_pincode}')")
            print(f"Phone valid: {checkout.is_phone_valid} (phone='{checkout.customer_phone}')")
            print(f"Payment selected: {checkout.is_payment_method_selected} (method='{checkout.payment_method}')")
            print(f"Items available: {checkout.is_items_available} (items count={len(items)})")
            print(f"=================================\n")
            
            return jsonify({
                'success': False,
                'message': 'Checkout validation failed',
                'validation_errors': {
                    'address_valid': checkout.is_address_valid,
                    'phone_valid': checkout.is_phone_valid,
                    'payment_selected': checkout.is_payment_method_selected,
                    'items_available': checkout.is_items_available
                }
            }), 400
        
        # All validations passed - create order
        total_amount = 0
        order_items = []
        
        for item in items:
            food = Food.query.get(item['food_id'])
            if not food:
                db.session.rollback()
                return jsonify({'error': f'Food item not found'}), 404
            
            quantity = int(item['quantity'])
            unit_price = float(item.get('price', food.price))
            total_price = unit_price * quantity
            total_amount += total_price
            
            order_item = OrderItem(
                id=str(uuid.uuid4()),
                food_id=food.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            order_items.append(order_item)
        
        # Create order
        order = Order(
            id=str(uuid.uuid4()),
            customer_id=user_id,
            order_number=generate_order_number(),
            total_amount=checkout.final_total,
            delivery_fee=checkout.delivery_fee,
            delivery_address=checkout.delivery_address,
            customer_phone=checkout.customer_phone,
            special_instructions=checkout.special_instructions,
            status='confirmed',
            payment_method=checkout.payment_method,
            estimated_delivery_time=datetime.utcnow() + timedelta(minutes=45)
        )
        
        for order_item in order_items:
            order.items.append(order_item)
        
        # Create delivery record
        delivery = Delivery(
            id=str(uuid.uuid4()),
            order_id=order.id,
            status='pending',
            estimated_time_minutes=45,
            delivery_location=checkout.delivery_address
        )
        
        # Update checkout status
        checkout.order_id = order.id
        checkout.checkout_status = 'confirmed'
        checkout.estimated_delivery_time = order.estimated_delivery_time
        
        db.session.add(order)
        db.session.add(delivery)
        db.session.add(checkout)
        db.session.commit()
        
        # Send confirmation emails (non-blocking)
        try:
            # Send order confirmation to user
            send_order_confirmation_email(
                user_email=user.email,
                user_name=user.name,
                order_number=order.order_number,
                order_details=order.to_dict(),
                total_amount=order.total_amount,
                estimated_delivery_time=order.estimated_delivery_time.strftime('%I:%M %p') if order.estimated_delivery_time else 'N/A',
                app=current_app
            )
            
            # Send order notification to admin
            from utils import send_admin_order_notification
            send_admin_order_notification(
                order_number=order.order_number,
                customer_name=user.name,
                customer_email=user.email,
                customer_phone=checkout.customer_phone,
                delivery_address=checkout.delivery_address,
                order_details=order.to_dict(),
                total_amount=order.total_amount,
                app=current_app
            )
            print(f"✓ Emails sent for order {order.order_number}")
        except Exception as e:
            print(f"⚠️ Email notification failed (non-blocking): {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order': order.to_dict(),
            'checkout': checkout.to_dict(),
            'order_number': order.order_number,
            'estimated_delivery': order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@checkout_bp.route('/summary', methods=['POST'])
@jwt_required()
def get_checkout_summary():
    """Get checkout summary with validation status"""
    try:
        user_id = get_jwt_identity()
        
        data = request.get_json()
        items = data.get('items', [])
        
        # Calculate totals
        subtotal = 0
        for item in items:
            subtotal += item.get('price', 0) * item.get('quantity', 0)
        
        tax_amount = round(subtotal * 0.05 * 100) / 100  # 5% tax
        delivery_fee = 50 if subtotal < 500 else 0  # Free delivery above 500
        final_total = subtotal + tax_amount + delivery_fee
        
        return jsonify({
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'delivery_fee': delivery_fee,
            'final_total': final_total,
            'discount_eligible': subtotal > 300  # Discount eligible above 300
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
