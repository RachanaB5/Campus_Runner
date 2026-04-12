#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.getcwd())

from utils import (
    build_order_confirmation_email_html,
    generate_order_invoice_pdf
)
from flask_mail import Message, Mail
from dotenv import load_dotenv
from flask import Flask

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Create minimal Flask app for mail context
app = Flask(__name__)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', True)
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@campusrunner.com')

recipient = 'kumarsrinidhi246@gmail.com'
print(f"\nSending Order Confirmation Email with PDF Invoice to {recipient}...\n")

# Order data
user_name = 'Kumar'
order_number = 'ORD-2026-04-13-001'
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

total_amount = 389
estimated_delivery_time = '30-45 mins'

# Generate HTML and PDF
print("1. Generating Order Confirmation HTML...")
html = build_order_confirmation_email_html(
    user_name=user_name,
    order_number=order_number,
    order_details=order_details,
    total_amount=total_amount,
    estimated_delivery_time=estimated_delivery_time,
    otp_details=otp_details
)
print("   Generated HTML email body")

print("\n2. Generating Invoice PDF...")
pdf_buffer = generate_order_invoice_pdf(
    user_name=user_name,
    order_number=order_number,
    order_details=order_details,
    total_amount=total_amount,
    estimated_delivery_time=estimated_delivery_time,
    otp_details=otp_details
)
print(f"   Generated PDF ({len(pdf_buffer.getvalue())} bytes)")

# Send email with PDF attachment
print(f"\n3. Sending Email with PDF Attachment...")
with app.app_context():
    try:
        mail = Mail(app)
        sender_email = app.config.get('MAIL_USERNAME') or app.config.get('MAIL_DEFAULT_SENDER')
        
        msg = Message(
            subject=f'Order Confirmation #{order_number} - Campus Runner',
            recipients=[recipient],
            html=html,
            sender=("Campus Runner", sender_email)
        )
        
        # Attach PDF
        pdf_buffer.seek(0)
        msg.attach(
            filename=f'{order_number}_Invoice.pdf',
            content_type='application/pdf',
            data=pdf_buffer.getvalue()
        )
        
        print(f"   Sending email with attachment from {sender_email}...")
        mail.send(msg)
        print(f"   SUCCESS! Email sent to {recipient}")
        print(f"   Attachment: {order_number}_Invoice.pdf")
        
    except Exception as e:
        print(f"   FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("Order Confirmation with Invoice PDF sent successfully!")
print("="*60)
