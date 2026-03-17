from flask_mail import Message
from threading import Thread
from datetime import datetime
import os
import traceback

def send_email_in_background(app, subject, recipients, html):
    """Send email in background thread with proper app context"""
    def send_email():
        try:
            with app.app_context():
                from flask_mail import Mail
                mail = Mail(app)
                
                # Use email as sender, Flask-Mail will use it with display name
                sender_email = app.config.get('MAIL_USERNAME', 'noreply@campusrunner.com')
                
                msg = Message(
                    subject=subject, 
                    recipients=recipients, 
                    html=html,
                    sender=("Campus Runner", sender_email)
                )
                
                print(f"📧 Sending email:")
                print(f"  From: {sender_email}")
                print(f"  To: {recipients}")
                print(f"  Subject: {subject}")
                
                mail.send(msg)
                print(f"✅ Email successfully sent to {recipients}")
        except Exception as e:
            print(f"❌ Error sending email to {recipients}: {str(e)}")
            print(f"📍 Traceback: {traceback.format_exc()}")
    
    thread = Thread(target=send_email)
    thread.daemon = True
    thread.start()

def send_order_confirmation_email(user_email, user_name, order_number, order_details, total_amount, estimated_delivery_time, app=None):
    """Send order confirmation email"""
    try:
        print(f"\n📧 Attempting to send order confirmation email to {user_email}")
        if app is None:
            from app import app as flask_app
            app = flask_app
        
        # Build email body
        items_html = ""
        for item in order_details.get('items', []):
            items_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.get('food_name', 'Item')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{item.get('quantity', 0)}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">₹{item.get('total_price', 0):.2f}</td>
            </tr>
            """
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                    .content {{ background: #f9f9f9; padding: 20px; }}
                    .order-number {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                    .section {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ff8c00; }}
                    .section-title {{ font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; }}
                    .status-badge {{ display: inline-block; background: #4CAF50; color: white; padding: 8px 12px; border-radius: 4px; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏃 Campus Runner</h1>
                        <p>Order Confirmed!</p>
                    </div>
                    
                    <div class="content">
                        <p>Hi <strong>{user_name}</strong>,</p>
                        <p>Thank you for your order! Your delicious food is being prepared.</p>
                        
                        <div class="section">
                            <div class="section-title">Order Details</div>
                            <div class="order-number">Order #{order_number}</div>
                            <p><span class="status-badge">CONFIRMED</span></p>
                            <p><strong>Estimated Delivery:</strong> {estimated_delivery_time}</p>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Order Items</div>
                            <table>
                                <thead>
                                    <tr style="background: #f0f0f0;">
                                        <th style="padding: 10px; text-align: left;">Item</th>
                                        <th style="padding: 10px; text-align: center;">Qty</th>
                                        <th style="padding: 10px; text-align: right;">Price</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items_html}
                                </tbody>
                                <tfoot>
                                    <tr style="background: #f0f0f0; font-weight: bold;">
                                        <td colspan="2" style="padding: 10px; text-align: right;">Total:</td>
                                        <td style="padding: 10px; text-align: right; color: #ff8c00; font-size: 18px;">₹{total_amount:.2f}</td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Delivery Address</div>
                            <p>{order_details.get('delivery_address', 'N/A')}</p>
                            <p><strong>Phone:</strong> {order_details.get('customer_phone', 'N/A')}</p>
                        </div>
                        
                        <p style="margin-top: 20px;">You can track your order status in the Campus Runner app.</p>
                    </div>
                    
                    <div class="footer">
                        <p>Campus Runner - Fast Food Delivery Service</p>
                        <p>© 2024 Campus Runner. All rights reserved.</p>
                        <p>Contact: support@campusrunner.com</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Create message
        subject = f"Order Confirmation #{order_number} - Campus Runner"
        
        # Send email asynchronously
        print(f"✓ Order confirmation email queued for {user_email}")
        send_email_in_background(app, subject, [user_email], html)
        return True
        
    except Exception as e:
        print(f"❌ Error creating confirmation email: {str(e)}")
        print(f"📍 Traceback: {traceback.format_exc()}")
        return False

def send_order_ready_notification(user_email, user_name, order_number, app=None):
    """Send order ready notification"""
    try:
        if app is None:
            from app import app as flask_app
            app = flask_app
            
        subject = f"Your Order #{order_number} is Ready! - Campus Runner"
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                    .content {{ background: #f9f9f9; padding: 20px; }}
                    .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Your Order is Ready!</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hi <strong>{user_name}</strong>,</p>
                        
                        <div class="alert">
                            <strong>Great News!</strong> Your order #{order_number} is ready for delivery. Our runner will pick it up shortly and bring it to you!
                        </div>
                        
                        <p>Keep an eye on the Campus Runner app for real-time tracking of your delivery.</p>
                    </div>
                    
                    <div class="footer">
                        <p>Campus Runner - Fast Food Delivery Service</p>
                        <p>© 2024 Campus Runner. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        send_email_in_background(app, subject, [user_email], html)
        return True
        
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return False

def send_welcome_email(user_email, user_name, app=None):
    """Send welcome email to new user"""
    try:
        if app is None:
            from app import app as flask_app
            app = flask_app
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                    .content {{ background: #f9f9f9; padding: 20px; }}
                    .section {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ff8c00; }}
                    .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; }}
                    .feature-item {{ margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Welcome to Campus Runner!</h1>
                        <p>Your favorite food delivery service</p>
                    </div>
                    
                    <div class="content">
                        <p>Hi <strong>{user_name}</strong>,</p>
                        
                        <p>Welcome to Campus Runner! We're thrilled to have you aboard. Get ready for fast, delicious food delivered right to your doorstep! 🍽️</p>
                        
                        <div class="section">
                            <div class="section-title" style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">Why Choose Campus Runner?</div>
                            <div class="feature-item">✓ Fast Delivery: Get your order in 30-45 minutes</div>
                            <div class="feature-item">✓ Wide Selection: Hundreds of dishes</div>
                            <div class="feature-item">✓ Best Prices: Great deals every day</div>
                            <div class="feature-item">✓ Rewards: Earn points with every order</div>
                        </div>
                        
                        <div class="section">
                            <p>Start ordering now and enjoy delicious meals from your favorite restaurants!</p>
                        </div>
                        
                        <p style="margin-top: 20px; text-align: center;">
                            <strong>Happy Ordering!</strong><br>
                            - The Campus Runner Team
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>Campus Runner - Fast Food Delivery Service</p>
                        <p>© 2024 Campus Runner. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        send_email_in_background(app, "Welcome to Campus Runner! 🎉", [user_email], html)
        return True
        
    except Exception as e:
        print(f"Error in send_welcome_email: {str(e)}")
        return False

def send_admin_order_notification(order_number, customer_name, customer_email, customer_phone, delivery_address, order_details, total_amount, app=None):
    """Send order notification to admin"""
    try:
        print(f"\n📧 Attempting to send admin notification for order {order_number}")
        if app is None:
            from app import app as flask_app
            app = flask_app
        
        admin_email = os.getenv('ADMIN_EMAIL', 'campusrunnerrvu@gmail.com')
        print(f"📬 Admin email target: {admin_email}")
        
        # Build items HTML
        items_html = ""
        if isinstance(order_details, dict) and 'items' in order_details:
            for item in order_details.get('items', []):
                items_html += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.get('food_name', 'Item')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{item.get('quantity', 0)}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">₹{item.get('total_price', 0):.2f}</td>
                </tr>
                """
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Courier New', monospace; color: #333; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #333; color: #ff8c00; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                    .content {{ background: #f5f5f5; padding: 20px; }}
                    .section {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border: 1px solid #ddd; }}
                    .section-title {{ font-size: 14px; font-weight: bold; color: #ff8c00; margin-bottom: 10px; text-transform: uppercase; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    .alert {{ background: #ffe6cc; border-left: 4px solid #ff8c00; padding: 12px; margin: 10px 0; border-radius: 4px; }}
                    .footer {{ background: #333; color: white; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 11px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>📋 NEW ORDER RECEIVED</h2>
                        <p>Order #: {order_number}</p>
                    </div>
                    
                    <div class="content">
                        <div class="alert">
                            <strong>⚠️ NEW ORDER:</strong> Please prepare this order immediately!
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Customer Information</div>
                            <p><strong>Name:</strong> {customer_name}</p>
                            <p><strong>Email:</strong> {customer_email}</p>
                            <p><strong>Phone:</strong> {customer_phone}</p>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Delivery Address</div>
                            <p>{delivery_address}</p>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Order Items</div>
                            <table>
                                <thead>
                                    <tr style="background: #f0f0f0;">
                                        <th style="padding: 8px; text-align: left;">Item</th>
                                        <th style="padding: 8px; text-align: center;">Qty</th>
                                        <th style="padding: 8px; text-align: right;">Price</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items_html}
                                </tbody>
                                <tfoot>
                                    <tr style="background: #f0f0f0; font-weight: bold;">
                                        <td colspan="2" style="padding: 10px; text-align: right;">Total:</td>
                                        <td style="padding: 10px; text-align: right; color: #ff8c00; font-size: 16px;">₹{total_amount:.2f}</td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Campus Runner Admin System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        print(f"✓ Admin notification queued for {admin_email}")
        send_email_in_background(app, f"🔔 NEW ORDER #{order_number} from Campus Runner", [admin_email], html)
        return True
        
    except Exception as e:
        print(f"❌ Error in send_admin_order_notification: {str(e)}")
        print(f"📍 Traceback: {traceback.format_exc()}")
        return False
