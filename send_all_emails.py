#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Change to backend directory
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.getcwd())

# Suppress emoji output from app.py during import
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from app import app
    from utils import (
        build_otp_email_html, 
        send_otp_email_sync, 
        send_welcome_email, 
        send_order_ready_notification,
        send_order_confirmation_email,
        send_admin_order_notification
    )
    
    recipient = 'kumarsrinidhi246@gmail.com'
    print(f"\nSending all email templates to {recipient}...\n")
    
    # 1. OTP Email (Profile Signup)
    print("1. Sending OTP Email (Profile Signup)...")
    with app.app_context():
        otp_html = build_otp_email_html(
            otp='482915',
            purpose='profile_signup',
            recipient_name='Kumar',
            extra_details=[
                {'label': 'Reason', 'value': 'Account Creation'},
                {'label': 'Time', 'value': 'April 13, 2026 10:30 AM'}
            ]
        )
        sent, err = send_otp_email_sync(
            app, 
            'Verify Your Campus Runner Account',
            [recipient],
            otp_html,
            otp_for_log='482915'
        )
        print(f"   Result: {'SUCCESS' if sent else 'FAILED'}\n")
    
    # 2. Welcome Email
    print("2. Sending Welcome Email...")
    with app.app_context():
        result = send_welcome_email(recipient, 'Kumar', app)
        print(f"   Result: {'QUEUED' if result else 'FAILED'}\n")
    
    # 3. Order Confirmation Email with OTPs
    print("3. Sending Order Confirmation Email...")
    with app.app_context():
        order_details = {
            'items': [
                {'food_name': 'Butter Chicken', 'quantity': 1, 'total_price': 249},
                {'food_name': 'Garlic Naan', 'quantity': 2, 'total_price': 80},
                {'food_name': 'Mango Lassi', 'quantity': 1, 'total_price': 60}
            ],
            'delivery_address': 'Room 234, North Block, Campus',
            'customer_phone': '+91-98765-43210'
        }
        
        otp_details = [
            {
                'label': 'Pickup OTP',
                'value': '5847',
                'hint': 'Show when runner collects from canteen',
                'accent': '#EA580C',
                'surface': '#FFF7ED'
            },
            {
                'label': 'Delivery OTP', 
                'value': '3921',
                'hint': 'Share only when runner delivers',
                'accent': '#16A34A',
                'surface': '#F0FDF4'
            }
        ]
        
        result = send_order_confirmation_email(
            recipient,
            'Kumar',
            'ORD-2026-04-13-001',
            order_details,
            389,
            '30-45 mins',
            app,
            otp_details
        )
        print(f"   Result: {'QUEUED' if result else 'FAILED'}\n")
    
    # 4. Order Ready Notification
    print("4. Sending Order Ready Notification...")
    with app.app_context():
        result = send_order_ready_notification(recipient, 'Kumar', 'ORD-2026-04-13-001', app)
        print(f"   Result: {'QUEUED' if result else 'FAILED'}\n")
    
    # 5. Admin Order Notification
    print("5. Sending Admin Order Notification...")
    with app.app_context():
        admin_result = send_admin_order_notification(
            'ORD-2026-04-13-001',
            'Kumar',
            recipient,
            '+91-98765-43210',
            'Room 234, North Block, Campus',
            order_details,
            389,
            app
        )
        print(f"   Result: {'QUEUED' if admin_result else 'FAILED'}\n")
    
    # 6. Password Reset OTP
    print("6. Sending Password Reset OTP Email...")
    with app.app_context():
        otp_html = build_otp_email_html(
            otp='629184',
            purpose='profile_password_reset',
            recipient_name='Kumar',
            extra_details=[
                {'label': 'Request Time', 'value': 'April 13, 2026 10:45 AM'},
                {'label': 'Action', 'value': 'Password Reset'}
            ]
        )
        sent, err = send_otp_email_sync(
            app,
            'Reset Your Campus Runner Password',
            [recipient],
            otp_html,
            otp_for_log='629184'
        )
        print(f"   Result: {'SUCCESS' if sent else 'FAILED'}\n")
    
    print("=" * 60)
    print("All email templates sent to kumarsrinidhi246@gmail.com!")
    print("=" * 60)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
