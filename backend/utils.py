from flask_mail import Message
from threading import Thread
from datetime import datetime
from html import escape
import os
import traceback
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


OTP_EMAIL_THEMES = {
        'profile_signup': {
                'subject': 'Verify Your Campus Runner Account',
                'eyebrow': 'Profile Security',
                'title': 'Confirm Your Account',
                'summary': 'Use this code to complete sign-up and activate your profile.',
                'accent': '#F97316',
                'accent_dark': '#C2410C',
                'surface': '#FFF7ED',
                'code_label': 'Verification Code',
                'code_hint': 'Enter this code to finish creating your account.',
                'footer': 'Never share this code with anyone. Campus Runner will never ask for it by phone or chat.',
        },
        'profile_password_reset': {
                'subject': 'Reset Your Campus Runner Password',
                'eyebrow': 'Account Recovery',
                'title': 'Reset Your Password',
                'summary': 'Use this code to verify your identity before creating a new password.',
                'accent': '#2563EB',
                'accent_dark': '#1D4ED8',
                'surface': '#EFF6FF',
                'code_label': 'Reset Code',
                'code_hint': 'Enter this code on the password reset screen.',
                'footer': 'If you did not request a password reset, you can safely ignore this email.',
        },
        'profile_update': {
                'subject': 'Confirm Your Profile Update',
                'eyebrow': 'Profile Update',
                'title': 'Verify Profile Changes',
                'summary': 'Use this code to confirm changes made to your profile details.',
                'accent': '#0EA5A4',
                'accent_dark': '#0F766E',
                'surface': '#ECFEFF',
                'code_label': 'Profile OTP',
                'code_hint': 'Enter this code to approve the profile update.',
                'footer': 'Only approve changes you initiated yourself.',
        },
        'order_pickup': {
                'subject': 'Pickup Verification Code for Your Order',
                'eyebrow': 'Order Pickup',
                'title': 'Confirm Pickup With the Runner',
                'summary': 'Show this code when the runner collects your order from the canteen.',
                'accent': '#EA580C',
                'accent_dark': '#C2410C',
                'surface': '#FFF7ED',
                'code_label': 'Pickup OTP',
                'code_hint': 'Use this code only when pickup verification is requested.',
                'footer': 'Keep this code private until it is needed for pickup verification.',
        },
        'order_delivery': {
                'subject': 'Delivery Verification Code for Your Order',
                'eyebrow': 'Order Delivery',
                'title': 'Confirm Your Delivery',
                'summary': 'Use this code to confirm the order was delivered to the correct person.',
                'accent': '#16A34A',
                'accent_dark': '#15803D',
                'surface': '#F0FDF4',
                'code_label': 'Delivery OTP',
                'code_hint': 'Share this code only when the runner asks for delivery verification.',
                'footer': 'Never share this code publicly. It is for delivery confirmation only.',
        },
}


def _normalize_otp_theme_key(value):
        if not value:
                return 'profile_signup'
        return str(value).strip().lower().replace(' ', '_').replace('-', '_')


def _get_otp_theme(value):
        return OTP_EMAIL_THEMES.get(_normalize_otp_theme_key(value), OTP_EMAIL_THEMES['profile_signup'])


def _brand_support_email(app=None):
        if app is not None:
                configured = (app.config.get('MAIL_SUPPORT_EMAIL') or '').strip()
                if configured:
                        return configured
                sender = (
                        (app.config.get('MAIL_USERNAME') or '').strip()
                        or (app.config.get('MAIL_DEFAULT_SENDER') or '').strip()
                )
                if sender:
                        return sender
        return (
                os.getenv('MAIL_SUPPORT_EMAIL', '').strip()
                or os.getenv('MAIL_USERNAME', '').strip()
                or os.getenv('EMAIL_ADDRESS', '').strip()
                or 'support@campusrunner.com'
        )


def _brand_logo_url(app=None):
        if app is not None:
                configured = (
                        app.config.get('MAIL_LOGO_URL')
                        or app.config.get('BRAND_LOGO_URL')
                        or app.config.get('APP_LOGO_URL')
                        or ''
                )
                configured = str(configured).strip()
                if configured:
                        return configured
        return (
                os.getenv('MAIL_LOGO_URL', '').strip()
                or os.getenv('BRAND_LOGO_URL', '').strip()
                or os.getenv('APP_LOGO_URL', '').strip()
        )


def _render_email_brand_header(app=None):
        logo_url = _brand_logo_url(app)
        if logo_url:
                safe_url = escape(logo_url, quote=True)
                return f'''
                                <tr>
                                    <td style="padding: 22px 28px; border-bottom: 1px solid #e6ebf1; background: #ffffff;">
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse: collapse;">
                                            <tr>
                                                <td style="vertical-align: middle; width: 56px;">
                                                    <img src="{safe_url}" alt="Campus Runner" style="width: 44px; height: 44px; border-radius: 10px; display: block;" />
                                                </td>
                                                <td style="vertical-align: middle;">
                                                    <div style="font-size: 24px; font-weight: 800; color: #111827; line-height: 1.1;">CampusRunner</div>
                                                    <div style="font-size: 12px; color: #6b7280; margin-top: 4px;">Campus food ordering and delivery</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                '''

        return '''
                                <tr>
                                    <td style="padding: 22px 28px; border-bottom: 1px solid #e6ebf1; background: #ffffff;">
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse: collapse;">
                                            <tr>
                                                <td style="vertical-align: middle; width: 56px;">
                                                    <div style="width: 44px; height: 44px; border-radius: 10px; background: linear-gradient(135deg, #ea580c 0%, #f97316 100%); color: #ffffff; text-align: center; line-height: 44px; font-size: 18px; font-weight: 800;">CR</div>
                                                </td>
                                                <td style="vertical-align: middle;">
                                                    <div style="font-size: 24px; font-weight: 800; color: #111827; line-height: 1.1;">CampusRunner</div>
                                                    <div style="font-size: 12px; color: #6b7280; margin-top: 4px;">Campus food ordering and delivery</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
        '''


def build_otp_email_html(otp, purpose, recipient_name=None, extra_details=None):
        theme = _get_otp_theme(purpose)
        safe_name = escape((recipient_name or 'Customer').strip())
        safe_otp = escape(str(otp))
        support_email = escape(_brand_support_email())
        brand_header = _render_email_brand_header()
        action_message = {
                'profile_signup': 'verify your email address',
                'profile_password_reset': 'reset your password',
                'profile_update': 'confirm your profile changes',
                'order_pickup': 'confirm order pickup',
                'order_delivery': 'confirm your delivery',
        }.get(_normalize_otp_theme_key(purpose), 'verify your account')

        details_html = ''
        for item in extra_details or []:
                if isinstance(item, dict):
                        label = escape(str(item.get('label', 'Detail')))
                        value = escape(str(item.get('value', '')))
                else:
                        label = escape(str(item[0]))
                        value = escape(str(item[1]))
                details_html += f'''
                        <tr>
                                <td style="padding: 10px 14px; border: 1px solid #e5e7eb;">
                                        <div style="font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;">{label}</div>
                                        <div style="font-size: 14px; color: #111827; font-weight: 600;">{value}</div>
                                </td>
                        </tr>
                '''

        details_section = ''
        if details_html:
                details_section = f'''
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse: collapse; margin: 18px 0 0 0;">
                    {details_html}
                </table>
                '''

        return f'''
        <html>
            <body style="margin:0; padding:0; background:#f6f9fc; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Ubuntu, sans-serif;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding: 24px 10px;">
                    <tr>
                        <td align="center">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 600px; background: #ffffff; border: 1px solid #e6ebf1;">
                                {brand_header}
                                <tr>
                                    <td style="padding: 28px 36px;">
                                        <div style="font-size: 25px; font-weight: 600; color: #111827; margin-bottom: 16px;">{escape(theme['title'])}</div>
                                        <div style="font-size: 16px; color: #4b5563; line-height: 1.65; margin-bottom: 14px;">Hi {safe_name},</div>
                                        <div style="font-size: 16px; color: #4b5563; line-height: 1.65; margin-bottom: 18px;">Use the following code to {action_message}:</div>

                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 10px 0 4px 0;">
                                            <tr>
                                                <td align="center" style="background: #f4f4f5; border-radius: 8px; padding: 22px 12px;">
                                                    <div style="font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #111827; font-family: monospace;">{safe_otp}</div>
                                                </td>
                                            </tr>
                                        </table>

                                        <div style="font-size: 13px; color: #6b7280; text-align: center; margin: 10px 0 6px 0;">This code expires in 10 minutes.</div>
                                        {details_section}

                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-top: 20px;">
                                            <tr>
                                                <td style="background: #fef3c7; border-radius: 8px; padding: 14px;">
                                                    <div style="font-size: 13px; color: #92400e; line-height: 1.7;">
                                                        <strong>Security Tips</strong><br/>
                                                        - Never share this code with anyone<br/>
                                                        - Campus Runner will never ask for OTP over phone<br/>
                                                        - This code is for one-time use only
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>

                                        <div style="font-size: 14px; color: #6b7280; line-height: 1.7; margin-top: 18px;">{escape(theme['footer'])}</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 22px 36px; border-top: 1px solid #e6ebf1;">
                                        <div style="font-size: 12px; line-height: 1.6; color: #8898aa;">Need help? Contact {support_email}</div>
                                        <div style="font-size: 12px; line-height: 1.6; color: #8898aa;">&copy; {datetime.now().year} Campus Runner. All rights reserved.</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        '''


def _mail_send_async() -> bool:
    v = os.getenv("MAIL_ASYNC_SEND")
    if v is None:
        return False
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def _smtp_credentials_configured(app):
    user = (app.config.get('MAIL_USERNAME') or '').strip()
    password = (app.config.get('MAIL_PASSWORD') or '').strip()
    return bool(user and password)


def send_otp_email_sync(app, subject, recipients, html, otp_for_log=None):
    """
    Send OTP mail synchronously so misconfiguration shows up immediately.
    Returns (sent: bool, error_message_or_none).
    If SMTP is not configured, logs otp_for_log to the console when provided.
    """
    try:
        with app.app_context():
            if not _smtp_credentials_configured(app):
                print("\n" + "=" * 64)
                print("  MAIL NOT CONFIGURED — verification email was not sent.")
                print("  Set MAIL_USERNAME + MAIL_PASSWORD (or EMAIL_ADDRESS + EMAIL_PASSWORD) in .env")
                if otp_for_log and recipients:
                    print(f"  OTP for {recipients[0]}: {otp_for_log}")
                print("=" * 64 + "\n")
                return False, "mail_not_configured"

            from app import mail as flask_mail

            sender_email = (app.config.get('MAIL_USERNAME') or app.config.get('MAIL_DEFAULT_SENDER') or '').strip()
            plain = None
            if otp_for_log:
                plain = f"Your verification code is: {otp_for_log}\n\nThis code expires in 10 minutes.\n"
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html,
                body=plain or "Please view the HTML version of this email.",
                sender=sender_email,
                reply_to=sender_email,
            )
            print(f"📧 Sending OTP email from {sender_email} to {recipients}")
            with flask_mail.connect() as connection:
                connection.send(msg)
            print(f"✅ OTP email sent to {recipients}")
            return True, None
    except Exception as e:
        print(f"❌ Error sending OTP email to {recipients}: {str(e)}")
        print(traceback.format_exc())
        if otp_for_log and recipients:
            print(f"  (after failure) OTP for {recipients[0]} was: {otp_for_log}")
        return False, str(e)


def send_email_in_background(app, subject, recipients, html):
    """Send transactional email. Defaults to synchronous SMTP so messages are not lost under the dev reloader."""
    def send_email():
        try:
            with app.app_context():
                if not _smtp_credentials_configured(app):
                    print(f"⚠️ Mail not configured; skipping background email to {recipients} ({subject})")
                    return
                from app import mail as flask_mail

                sender_email = (
                    (app.config.get('MAIL_USERNAME') or '').strip()
                    or (app.config.get('MAIL_DEFAULT_SENDER') or 'noreply@campusrunner.com')
                )

                msg = Message(
                    subject=subject,
                    recipients=recipients,
                    html=html,
                    body="Please view the HTML version of this email.",
                    sender=sender_email,
                    reply_to=sender_email,
                )

                print(f"📧 Sending email:")
                print(f"  From: {sender_email}")
                print(f"  To: {recipients}")
                print(f"  Subject: {subject}")

                with flask_mail.connect() as connection:
                    connection.send(msg)
                print(f"✅ Email successfully sent to {recipients}")
        except Exception as e:
            print(f"❌ Error sending email to {recipients}: {str(e)}")
            print(f"📍 Traceback: {traceback.format_exc()}")

    if _mail_send_async():
        thread = Thread(target=send_email, name="mail-send")
        thread.daemon = False
        thread.start()
    else:
        send_email()


def build_order_confirmation_email_html(user_name, order_number, order_details, total_amount, estimated_delivery_time, otp_details=None):
    support_email = escape(_brand_support_email())
    brand_header = _render_email_brand_header()
    items_html = ""
    for item in order_details.get('items', []):
        items_html += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px 0; color: #111827;">{escape(str(item.get('food_name', 'Item')))}</td>
            <td style="padding: 12px 0; text-align: center; color: #4b5563;">{escape(str(item.get('quantity', 0)))}</td>
            <td style="padding: 12px 0; text-align: right; color: #111827;">Rs. {float(item.get('total_price', 0)):.2f}</td>
        </tr>
        """

    otp_cards_html = ""
    for otp_item in otp_details or []:
        label = escape(str(otp_item.get('label', 'OTP')))
        value = escape(str(otp_item.get('value', '')))
        hint = escape(str(otp_item.get('hint', '')))
        accent = otp_item.get('accent', '#1f2937')
        surface = otp_item.get('surface', '#f9fafb')
        otp_cards_html += f"""
        <tr>
          <td style="padding: 14px; background: {surface}; border: 1px solid #e5e7eb; border-radius: 8px;">
            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #6b7280; margin-bottom: 6px;">{label}</div>
            <div style="font-size: 30px; letter-spacing: 0.26em; font-weight: 700; color: {accent}; line-height: 1.2; margin-bottom: 8px;">{value}</div>
            <div style="font-size: 13px; line-height: 1.6; color: #4b5563;">{hint}</div>
          </td>
        </tr>
        """

    otp_section = ""
    if otp_cards_html:
        otp_section = f"""
        <div style="margin: 24px 0 8px 0;">
          <div style="font-size: 14px; font-weight: 700; color: #111827; margin-bottom: 12px;">Verification Codes</div>
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse: separate; border-spacing: 0 8px;">
            {otp_cards_html}
          </table>
        </div>
        """

    return f"""
    <html>
      <body style="margin:0; padding:0; background:#f6f9fc; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Ubuntu, sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding: 24px 10px;">
          <tr>
            <td align="center">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 620px; background:#ffffff; border: 1px solid #e6ebf1;">
                                {brand_header}

                <tr>
                  <td style="padding: 24px 32px; background: #f0fdf4; text-align: center;">
                    <div style="font-size: 28px; color: #16a34a; line-height: 1; margin-bottom: 10px;">&#10003;</div>
                    <div style="font-size: 24px; font-weight: 600; color: #16a34a; margin-bottom: 8px;">Order Confirmed</div>
                    <div style="font-size: 15px; color: #166534;">Thank you for your order. We are preparing it now.</div>
                  </td>
                </tr>

                <tr>
                  <td style="padding: 28px 32px;">
                    <div style="font-size: 16px; color: #4b5563; line-height: 1.65; margin-bottom: 16px;">Hi {escape(str(user_name))},</div>

                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 22px;">
                      <tr>
                        <td style="padding: 14px;">
                          <div style="font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.08em;">Order Number</div>
                          <div style="font-size: 18px; font-weight: 700; color: #111827; margin: 6px 0 12px 0;">#{escape(str(order_number))}</div>
                          <div style="font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.08em;">Estimated Delivery</div>
                          <div style="font-size: 15px; color: #111827; margin-top: 6px;">{escape(str(estimated_delivery_time))}</div>
                        </td>
                      </tr>
                    </table>

                    {otp_section}

                    <div style="font-size: 16px; font-weight: 600; color: #111827; margin-bottom: 10px;">Order Summary</div>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse: collapse; margin-bottom: 16px;">
                      <tr style="border-bottom: 1px solid #d1d5db;">
                        <th style="padding: 10px 0; text-align: left; font-size: 13px; color: #6b7280;">Item</th>
                        <th style="padding: 10px 0; text-align: center; font-size: 13px; color: #6b7280;">Qty</th>
                        <th style="padding: 10px 0; text-align: right; font-size: 13px; color: #6b7280;">Price</th>
                      </tr>
                      {items_html}
                      <tr style="border-top: 1px solid #d1d5db;">
                        <td colspan="2" style="padding: 12px 0; text-align: right; font-weight: 700; color: #111827;">Total</td>
                        <td style="padding: 12px 0; text-align: right; font-weight: 700; color: #111827;">Rs. {float(total_amount):.2f}</td>
                      </tr>
                    </table>

                    <div style="font-size: 16px; font-weight: 600; color: #111827; margin-bottom: 10px;">Shipping Address</div>
                    <div style="font-size: 14px; line-height: 1.7; color: #4b5563; background:#f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px;">
                      {escape(str(order_details.get('delivery_address', 'N/A')))}<br/>
                      Phone: {escape(str(order_details.get('customer_phone', 'N/A')))}
                    </div>
                  </td>
                </tr>

                <tr>
                  <td style="padding: 22px 32px; border-top: 1px solid #e6ebf1;">
                                        <div style="font-size: 12px; color:#8898aa; line-height: 1.6;">Questions about your order? Contact {support_email}</div>
                    <div style="font-size: 12px; color:#8898aa; line-height: 1.6;">&copy; {datetime.now().year} Campus Runner. All rights reserved.</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

def send_order_confirmation_email_with_invoice_async(app, user_email, user_name, order_number, order_details, total_amount, estimated_delivery_time, otp_details=None):
    """Send order confirmation email with PDF invoice in background thread with proper app context"""
    def send_email_with_invoice():
        try:
            with app.app_context():
                if not _smtp_credentials_configured(app):
                    print(f"⚠️ Mail not configured; skipping order confirmation email to {user_email}")
                    return
                
                from flask_mail import Mail
                mail = Mail(app)
                
                sender_email = (
                    (app.config.get('MAIL_USERNAME') or '').strip()
                    or (app.config.get('MAIL_DEFAULT_SENDER') or 'noreply@campusrunner.com')
                )
                
                # Build HTML body
                html = build_order_confirmation_email_html(
                    user_name=user_name,
                    order_number=order_number,
                    order_details=order_details,
                    total_amount=total_amount,
                    estimated_delivery_time=estimated_delivery_time,
                    otp_details=otp_details,
                )
                
                # Generate PDF invoice
                pdf_buffer = generate_order_invoice_pdf(
                    user_name=user_name,
                    order_number=order_number,
                    order_details=order_details,
                    total_amount=total_amount,
                    estimated_delivery_time=estimated_delivery_time,
                    otp_details=otp_details,
                )
                
                # Create message with HTML body
                subject = f"Order Confirmation #{order_number} - Campus Runner"
                msg = Message(
                    subject=subject,
                    recipients=[user_email],
                    html=html,
                    sender=("Campus Runner", sender_email),
                )
                
                # Attach PDF invoice if generated successfully
                if pdf_buffer:
                    pdf_filename = f"{order_number}_Invoice.pdf"
                    msg.attach(pdf_filename, "application/pdf", pdf_buffer.getvalue())
                    print(f"📎 Attached PDF invoice: {pdf_filename}")
                else:
                    print(f"⚠️ PDF invoice generation failed; sending email without attachment")
                
                print(f"📧 Sending order confirmation with invoice:")
                print(f"  From: {sender_email}")
                print(f"  To: {user_email}")
                print(f"  Subject: {subject}")
                
                mail.send(msg)
                print(f"✅ Order confirmation email sent to {user_email}")
        except Exception as e:
            print(f"❌ Error sending order confirmation email to {user_email}: {str(e)}")
            print(f"📍 Traceback: {traceback.format_exc()}")
    
    thread = Thread(target=send_email_with_invoice)
    thread.daemon = True
    thread.start()


def send_order_confirmation_email(user_email, user_name, order_number, order_details, total_amount, estimated_delivery_time, app=None, otp_details=None):
    """Send order confirmation email with PDF invoice attachment."""
    try:
        print(f"\n📧 Attempting to send order confirmation email to {user_email}")
        if app is None:
            from app import app as flask_app
            app = flask_app

        # Send email with PDF invoice in background
        send_order_confirmation_email_with_invoice_async(
            app=app,
            user_email=user_email,
            user_name=user_name,
            order_number=order_number,
            order_details=order_details,
            total_amount=total_amount,
            estimated_delivery_time=estimated_delivery_time,
            otp_details=otp_details,
        )
        
        print(f"✓ Order confirmation email with invoice queued for {user_email}")
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
            
        safe_name = escape((user_name or 'there').strip())
        safe_order = escape(str(order_number))
        support_email = escape(_brand_support_email(app))
        brand_header = _render_email_brand_header(app)
        
        subject = f"Your Order #{order_number} is Ready! - Campus Runner"
        
        html = f"""
        <html>
            <body style="margin:0; padding:0; background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); font-family: Arial, Helvetica, sans-serif; color:#0f172a;">
                <div style="display:none; max-height:0; overflow:hidden; opacity:0; color:transparent;">
                    Your Campus Runner order is ready for pickup!
                </div>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); padding: 32px 12px;">
                    <tr>
                        <td align="center">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 680px; background: #ffffff; border-radius: 28px; overflow: hidden; box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12); border: 1px solid rgba(15, 23, 42, 0.06);">
                                {brand_header}
                                <tr>
                                    <td style="background: linear-gradient(135deg, #16A34A 0%, #15803D 100%); padding: 28px 32px; color:#ffffff;">
                                        <div style="font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; opacity: 0.9; margin-bottom: 10px;">Great News!</div>
                                        <div style="font-size: 30px; font-weight: 800; line-height: 1.2; margin-bottom: 8px;">Your Order is Ready</div>
                                        <div style="font-size: 15px; line-height: 1.6; max-width: 540px; opacity: 0.95;">Our runner is on their way to collect your delicious meal from the canteen!</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 32px; background: #ffffff;">
                                        <div style="margin-bottom: 18px; font-size: 16px; line-height: 1.7; color:#334155;">
                                            Hi <strong style="color:#0f172a;">{safe_name}</strong>,
                                            <br />
                                            Your order is ready and being prepared for delivery. A runner will pick it up from the canteen shortly!
                                        </div>

                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 24px 0; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 20px 16px; background: #F0FDF4; border: 2px solid #16A34A; border-radius: 20px; text-align: center;">
                                                    <div style="font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: #15803D; font-weight: 800; margin-bottom: 10px;">Order Number</div>
                                                    <div style="font-size: 36px; font-weight: 900; color: #15803D; margin-bottom: 8px;">#{safe_order}</div>
                                                    <div style="font-size: 13px; color: #334155; line-height: 1.6;">Expected delivery in 15-20 minutes. Keep an eye on the app for real-time updates!</div>
                                                </td>
                                            </tr>
                                        </table>

                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 24px 0;">
                                            <tr>
                                                <td style="padding: 16px; background: #F0FDF4; border: 1px solid rgba(0,0,0,0.05); border-radius: 20px; margin-bottom: 12px;">
                                                    <div style="font-size: 14px; font-weight: 800; color: #16A34A; margin-bottom: 6px;">What's Next?</div>
                                                    <div style="font-size: 14px; line-height: 1.7; color: #334155;">
                                                        1. Runner picks up your order from the canteen<br/>
                                                        2. Real-time tracking available in your app<br/>
                                                        3. Receive your order fresh and hot!
                                                    </div>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 16px; background: #F0FDF4; border: 1px solid rgba(0,0,0,0.05); border-radius: 20px;">
                                                    <div style="font-size: 14px; font-weight: 800; color: #16A34A; margin-bottom: 6px;">Pro Tips</div>
                                                    <div style="font-size: 14px; line-height: 1.7; color: #334155;">
                                                        - Be ready to provide your delivery OTP when the runner arrives<br/>
                                                        - Make sure your phone is reachable for the runner<br/>
                                                        - Check the app for live delivery updates
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>

                                        <div style="margin-top: 20px; font-size: 13px; line-height: 1.7; color:#64748b;">
                                            Questions? Contact our support team at {support_email}. We're here to help!
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 18px 32px 28px 32px; background: #ffffff; border-top: 1px solid rgba(15, 23, 42, 0.06);">
                                        <div style="font-size: 12px; line-height: 1.7; color:#94a3b8; text-align:center;">
                                            Campus Runner - Real-time food delivery for campus community
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
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
        
        safe_name = escape((user_name or 'Customer').strip())
        support_email = escape(_brand_support_email(app))
        brand_header = _render_email_brand_header(app)
        
        html = f"""
        <html>
            <body style="margin:0; padding:0; background:#f6f9fc; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Ubuntu, sans-serif;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding: 24px 10px;">
                    <tr>
                        <td align="center">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 600px; background: #ffffff; border: 1px solid #e6ebf1;">
                                {brand_header}

                                <tr>
                                    <td style="background: #1a1a1a; padding: 40px 36px; text-align: center;">
                                        <div style="font-size: 30px; font-weight: 700; color: #ffffff; margin-bottom: 8px;">Welcome to Campus Runner!</div>
                                        <div style="font-size: 16px; color: #a3a3a3;">We are thrilled to have you join our community</div>
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding: 30px 36px;">
                                        <div style="font-size: 16px; color: #4b5563; line-height: 1.65; margin-bottom: 14px;">Hi {safe_name},</div>
                                        <div style="font-size: 16px; color: #4b5563; line-height: 1.65; margin-bottom: 20px;">Your account has been successfully created. You can now browse menus, track orders, and earn rewards with every purchase.</div>

                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 20px 0; border-collapse: separate; border-spacing: 0 10px;">
                                            <tr><td style="padding: 14px; background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px;"><strong style="color:#111827;">Browse Canteens</strong><div style="margin-top:6px; color:#6b7280; font-size:14px;">Explore dishes from your favorite campus spots.</div></td></tr>
                                            <tr><td style="padding: 14px; background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px;"><strong style="color:#111827;">Fast Delivery</strong><div style="margin-top:6px; color:#6b7280; font-size:14px;">Track your runner in real-time from preparation to doorstep.</div></td></tr>
                                            <tr><td style="padding: 14px; background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px;"><strong style="color:#111827;">Rewards</strong><div style="margin-top:6px; color:#6b7280; font-size:14px;">Collect points and unlock special offers.</div></td></tr>
                                        </table>

                                        <div style="font-size: 14px; color:#6b7280; line-height: 1.7;">Need help? Contact {support_email} anytime.</div>
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding: 22px 36px; border-top: 1px solid #e6ebf1;">
                                        <div style="font-size: 12px; color: #8898aa; line-height: 1.6;">&copy; {datetime.now().year} Campus Runner. All rights reserved.</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        send_email_in_background(app, "Welcome to Campus Runner!", [user_email], html)
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
        
        safe_order = escape(str(order_number))
        safe_customer = escape(str(customer_name))
        safe_email = escape(str(customer_email))
        safe_phone = escape(str(customer_phone))
        safe_address = escape(str(delivery_address))
        
        # Build items HTML
        items_html = ""
        if isinstance(order_details, dict) and 'items' in order_details:
            for item in order_details.get('items', []):
                item_name = escape(str(item.get('food_name', 'Item')))
                item_qty = item.get('quantity', 0)
                item_price = float(item.get('total_price', 0))
                items_html += f"""
                <tr style="border-bottom: 1px solid rgba(15, 23, 42, 0.1);">
                    <td style="padding: 12px 0;">{item_name}</td>
                    <td style="padding: 12px 0; text-align: center;">{item_qty}</td>
                    <td style="padding: 12px 0; text-align: right;">Rs. {item_price:.2f}</td>
                </tr>
                """
        
        html = f"""
        <html>
            <body style="margin:0; padding:0; background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); font-family: Arial, Helvetica, sans-serif; color:#e2e8f0;">
                <div style="display:none; max-height:0; overflow:hidden; opacity:0; color:transparent;">
                    New Campus Runner order #{order_number} received
                </div>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); padding: 32px 12px;">
                    <tr>
                        <td align="center">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 780px; background: #0f172a; border-radius: 28px; overflow: hidden; box-shadow: 0 24px 60px rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 165, 0, 0.2);">
                                <tr>
                                    <td style="background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%); padding: 28px 32px; color:#ffffff;">
                                        <div style="font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; opacity: 0.9; margin-bottom: 10px;">New Order Alert</div>
                                        <div style="font-size: 30px; font-weight: 800; line-height: 1.2; margin-bottom: 8px;">Order #{safe_order} Received</div>
                                        <div style="font-size: 15px; line-height: 1.6; max-width: 540px; opacity: 0.95;">Immediate action required. Process this order right away!</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 32px; background: #0f172a;">
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 0 0 24px 0; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 16px; background: rgba(234, 88, 12, 0.1); border-left: 4px solid #ea580c; border-radius: 12px;">
                                                    <div style="font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #fbbf24; font-weight: 800; margin-bottom: 8px;">Priority</div>
                                                    <div style="font-size: 15px; color: #fca5a5; line-height: 1.6;">Begin preparation immediately. Customer is waiting!</div>
                                                </td>
                                            </tr>
                                        </table>

                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 24px 0; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 18px 16px; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(234, 88, 12, 0.3); border-radius: 16px; margin-bottom: 16px;">
                                                    <div style="font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #94a3b8; font-weight: 800; margin-bottom: 10px;">Customer Information</div>
                                                    <div style="font-size: 14px; line-height: 1.8; color: #cbd5e1;">
                                                        <strong style="color: #fbbf24;">Name:</strong> {safe_customer}<br/>
                                                        <strong style="color: #fbbf24;">Email:</strong> {safe_email}<br/>
                                                        <strong style="color: #fbbf24;">Phone:</strong> {safe_phone}
                                                    </div>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 18px 16px; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(234, 88, 12, 0.3); border-radius: 16px;">
                                                    <div style="font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #94a3b8; font-weight: 800; margin-bottom: 10px;">Delivery Address</div>
                                                    <div style="font-size: 14px; line-height: 1.8; color: #cbd5e1;">
                                                        {safe_address}
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>

                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 24px 0; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 18px 16px; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(234, 88, 12, 0.3); border-radius: 16px;">
                                                    <div style="font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #94a3b8; font-weight: 800; margin-bottom: 12px;">Order Items</div>
                                                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse: collapse;">
                                                        <tr style="background: rgba(234, 88, 12, 0.1); border-bottom: 2px solid rgba(234, 88, 12, 0.3);">
                                                            <th style="padding: 10px 0; text-align: left; color: #fbbf24; font-weight: 800; font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase;">Item</th>
                                                            <th style="padding: 10px 0; text-align: center; color: #fbbf24; font-weight: 800; font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase;">Qty</th>
                                                            <th style="padding: 10px 0; text-align: right; color: #fbbf24; font-weight: 800; font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase;">Price</th>
                                                        </tr>
                                                        {items_html}
                                                        <tr style="background: rgba(234, 88, 12, 0.15); border-top: 2px solid rgba(234, 88, 12, 0.3);">
                                                            <td colspan="2" style="padding: 12px 0; text-align: right; font-weight: 800; color: #fbbf24;">Total:</td>
                                                            <td style="padding: 12px 0; text-align: right; font-size: 18px; font-weight: 900; color: #ea580c;">Rs. {float(total_amount):.2f}</td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>

                                        <div style="margin-top: 24px; padding: 16px; background: rgba(251, 191, 36, 0.1); border-left: 4px solid #fbbf24; border-radius: 12px;">
                                            <div style="font-size: 13px; line-height: 1.8; color: #cbd5e1;">
                                                <strong style="color: #fbbf24;">Next Steps:</strong><br/>
                                                1. Verify all items are in stock<br/>
                                                2. Begin order preparation immediately<br/>
                                                3. Notify runner when order is ready<br/>
                                                4. Update status in Campus Runner admin dashboard
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 18px 32px 28px 32px; background: #0f172a; border-top: 1px solid rgba(234, 88, 12, 0.2);">
                                        <div style="font-size: 12px; line-height: 1.7; color:#64748b; text-align:center;">
                                            Campus Runner Admin Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        print(f"✓ Admin notification queued for {admin_email}")
        send_email_in_background(app, f"NEW ORDER #{order_number} from Campus Runner", [admin_email], html)
        return True
        
    except Exception as e:
        print(f"❌ Error in send_admin_order_notification: {str(e)}")
        print(f"📍 Traceback: {traceback.format_exc()}")
        return False


def generate_order_invoice_pdf(user_name, order_number, order_details, total_amount, estimated_delivery_time, otp_details=None):
    """Generate a professional PDF invoice for an order."""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.75*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=2,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )
        
        tagline_style = ParagraphStyle(
            'Tagline',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#64748B'),
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=6
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#EA580C'),
            spaceAfter=10,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Company Header with Professional Branding
        header_data = [
            ['CAMPUS RUNNER\nCampus Food Delivery', 'INVOICE', f'INV-{datetime.now().strftime("%Y%m%d")}-{order_number.split("-")[-1].zfill(5)}'],
        ]
        header_table = Table(header_data, colWidths=[2.5*inch, 0.8*inch, 2.2*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#EA580C')),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('VALIGN', (0, 0), (-1, 0), 'TOP'),
            ('ALIGN', (1, 0), (-1, 0), 'RIGHT'),
            ('FONTNAME', (1, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (-1, 0), 10),
            ('TEXTCOLOR', (1, 0), (-1, 0), colors.HexColor('#EA580C')),
            ('GRID', (0, 0), (-1, 0), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.1*inch))
        
        # Company Details
        company_data = [
            ['Campus Runner Pvt. Ltd.\nReg: CR-2026-001234-IN\nGSTIN: 27AABCT1234H1Z0', f'Invoice Date: {datetime.now().strftime("%d %b %Y")}\nInvoice Time: {datetime.now().strftime("%H:%M %p")}'],
        ]
        company_table = Table(company_data, colWidths=[3*inch, 3*inch])
        company_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#475569')),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, 0), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ]))
        story.append(company_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Order Info Section
        story.append(Paragraph('ORDER INFORMATION', heading_style))
        
        order_info_data = [
            ['Order Number:', f'#{escape(str(order_number))}', 'Order Date:', datetime.now().strftime('%d %B %Y')],
            ['Customer Name:', escape(str(user_name)), 'Status:', 'CONFIRMED'],
            ['Estimated Delivery:', estimated_delivery_time, 'Payment Mode:', 'Online'],
        ]
        
        order_info_table = Table(order_info_data, colWidths=[1.2*inch, 1.8*inch, 1.2*inch, 1.8*inch])
        order_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EFF6FF')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#EFF6FF')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 9),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 9),
            ('FONT', (3, 0), (3, -1), 'Helvetica', 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        story.append(order_info_table)
        story.append(Spacer(1, 0.2*inch))
        
        order_info_table = Table(order_info_data, colWidths=[1.3*inch, 1.7*inch, 1.3*inch, 1.7*inch])
        order_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F8FAFC')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('FONT', (3, 0), (3, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ]))
        story.append(order_info_table)
        story.append(Spacer(1, 0.25*inch))
        
        # Order Items Section
        story.append(Paragraph('ORDER ITEMS', heading_style))
        
        items_data = [['Item', 'Qty', 'Unit Price', 'Total']]
        for item in order_details.get('items', []):
            items_data.append([
                escape(str(item.get('food_name', 'Item'))),
                str(item.get('quantity', 0)),
                f"Rs. {float(item.get('total_price', 0)) / item.get('quantity', 1):.2f}",
                f"Rs. {float(item.get('total_price', 0)):.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[2.8*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EA580C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Totals Section
        totals_data = [
            ['Subtotal:', '', '', f"Rs. {float(total_amount):.2f}"],
            ['Tax (Included):', '', '', 'Rs. 0.00'],
            ['TOTAL AMOUNT:', '', '', f"Rs. {float(total_amount):.2f}"],
        ]
        
        totals_table = Table(totals_data, colWidths=[2.8*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 1), 'Helvetica'),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, 1), 'Helvetica'),
            ('FONTNAME', (3, 2), (3, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 1), 10),
            ('FONTSIZE', (0, 2), (-1, 2), 12),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#EA580C')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#FFF7ED')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.25*inch))
        
        # OTP Verification Codes Section
        if otp_details:
            story.append(Paragraph('VERIFICATION CODES', heading_style))
            
            otp_data = []
            for otp_item in otp_details:
                otp_data.append([
                    escape(str(otp_item.get('label', 'Code'))),
                    escape(str(otp_item.get('value', ''))),
                    escape(str(otp_item.get('hint', '')))
                ])
            
            otp_table = Table(otp_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
            otp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16A34A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0FDF4')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#86EFAC')),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            story.append(otp_table)
            story.append(Spacer(1, 0.25*inch))
        
        # Delivery Address Section
        story.append(Paragraph('DELIVERY ADDRESS', heading_style))
        
        address_data = [
            [escape(str(order_details.get('delivery_address', 'N/A')))],
            ['Phone: ' + escape(str(order_details.get('customer_phone', 'N/A')))],
        ]
        
        address_table = Table(address_data, colWidths=[6*inch])
        address_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BFE7FF')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(address_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Paragraph('Campus Runner - Fast Food Delivery for Campus Life', ParagraphStyle('footer', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#94A3B8'), alignment=TA_CENTER)))
        story.append(Paragraph('This invoice was generated on ' + datetime.now().strftime('%B %d, %Y at %H:%M %p'), ParagraphStyle('footer2', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#CBD5E1'), alignment=TA_CENTER)))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"❌ Error generating invoice PDF: {str(e)}")
        print(f"📍 Traceback: {traceback.format_exc()}")
        return None


def save_order_invoice_pdf(user_name, order_number, order_details, total_amount, estimated_delivery_time, otp_details=None, output_path=None):
    """Save order invoice PDF to file."""
    try:
        pdf_buffer = generate_order_invoice_pdf(
            user_name=user_name,
            order_number=order_number,
            order_details=order_details,
            total_amount=total_amount,
            estimated_delivery_time=estimated_delivery_time,
            otp_details=otp_details
        )
        
        if pdf_buffer is None:
            return False
        
        if output_path is None:
            output_path = f"order_invoice_{order_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"PDF Invoice saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving PDF: {str(e)}")
        return False


def send_runner_otp_notification(runner_email, runner_name, order_number, pickup_otp, delivery_otp, pickup_location, delivery_address, app=None):
    """Send OTP codes to assigned runner (separate from customer email)"""
    try:
        if app is None:
            from app import app as flask_app
            app = flask_app
        
        safe_runner = escape((runner_name or 'Runner').strip())
        safe_order = escape(str(order_number))
        safe_pickup = escape(str(pickup_location or 'Canteen'))
        safe_delivery = escape(str(delivery_address or 'Delivery Address'))
        support_email = escape(_brand_support_email(app))
        brand_header = _render_email_brand_header(app)
        
        html = f"""
        <html>
            <body style="margin:0; padding:0; background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); font-family: Arial, Helvetica, sans-serif; color:#0f172a;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); padding: 32px 12px;">
                    <tr>
                        <td align="center">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 680px; background: #ffffff; border-radius: 28px; overflow: hidden; box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12); border: 1px solid rgba(15, 23, 42, 0.06);">
                                {brand_header}
                                <tr>
                                    <td style="background: linear-gradient(135deg, #0EA5A4 0%, #0891B2 100%); padding: 28px 32px; color:#ffffff;">
                                        <div style="font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; opacity: 0.9; margin-bottom: 10px;">Order Pickup Assignment</div>
                                        <div style="font-size: 30px; font-weight: 800; line-height: 1.2; margin-bottom: 8px;">New Order #{safe_order}</div>
                                        <div style="font-size: 15px; line-height: 1.6; max-width: 540px; opacity: 0.95;">You have been assigned to pick up and deliver this order. Use the OTP codes below for verification.</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 32px; background: #ffffff;">
                                        <div style="margin-bottom: 18px; font-size: 16px; line-height: 1.7; color:#334155;">
                                            Hi <strong style="color:#0f172a;">{safe_runner}</strong>,
                                            <br />
                                            You have been assigned order #{safe_order}. Please use the OTP codes below when collecting the order from the canteen and when delivering to the customer.
                                        </div>

                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 24px 0;">
                                            <tr>
                                                <td style="padding: 20px 16px; background: #FEF3C7; border: 2px solid #F59E0B; border-radius: 20px; margin-bottom: 16px;">
                                                    <div style="font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: #92400E; font-weight: 800; margin-bottom: 8px;">Pickup OTP - From Canteen</div>
                                                    <div style="font-size: 48px; letter-spacing: 0.08em; font-weight: 900; color: #F59E0B; font-family: monospace;">{escape(str(pickup_otp))}</div>
                                                    <div style="font-size: 13px; color: #78350F; line-height: 1.6; margin-top: 12px;">Pickup Location: {safe_pickup}</div>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 20px 16px; background: #D1FAE5; border: 2px solid #10B981; border-radius: 20px;">
                                                    <div style="font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: #065F46; font-weight: 800; margin-bottom: 8px;">Delivery OTP - To Customer</div>
                                                    <div style="font-size: 48px; letter-spacing: 0.08em; font-weight: 900; color: #10B981; font-family: monospace;">{escape(str(delivery_otp))}</div>
                                                    <div style="font-size: 13px; color: #047857; line-height: 1.6; margin-top: 12px;">Delivery Address: {safe_delivery}</div>
                                                </td>
                                            </tr>
                                        </table>

                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 24px 0;">
                                            <tr>
                                                <td style="padding: 18px 16px; background: #f8fafc; border-radius: 18px; border: 1px solid rgba(15, 23, 42, 0.06);">
                                                    <div style="font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: #64748b; font-weight: 800; margin-bottom: 8px;">Your Responsibilities</div>
                                                    <div style="font-size: 14px; line-height: 1.8; color: #334155;">
                                                        1. Navigate to pickup location<br/>
                                                        2. Enter Pickup OTP {escape(str(pickup_otp))} at canteen<br/>
                                                        3. Collect the order securely<br/>
                                                        4. Navigate to delivery address<br/>
                                                        5. Enter Delivery OTP {escape(str(delivery_otp))} with customer
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>

                                        <div style="margin-top: 20px; font-size: 13px; line-height: 1.7; color:#64748b;">
                                            Track this order in your runner dashboard. Questions? Contact support at {support_email}.
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 18px 32px 28px 32px; background: #ffffff; border-top: 1px solid rgba(15, 23, 42, 0.06);">
                                        <div style="font-size: 12px; line-height: 1.7; color:#94a3b8; text-align:center;">
                                            Campus Runner - Delivery Network Operations
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        subject = f"New Pickup Assignment: Order #{order_number} - Campus Runner"
        send_email_in_background(app, subject, [runner_email], html)
        print(f"✓ Runner OTP notification queued for {runner_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending runner OTP: {str(e)}")
        print(f"📍 Traceback: {traceback.format_exc()}")
        return False
