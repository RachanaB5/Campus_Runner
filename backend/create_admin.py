from app import app
from models import db, User
import uuid

with app.app_context():
    # Create admin with consistent credentials
    admin_email = 'admin@rvu.edu.in'
    
    # Delete old admin if using different email
    old_admin = User.query.filter_by(email='admin@rvu.edu.in').first()
    if old_admin:
        db.session.delete(old_admin)
        db.session.commit()
        print("✓ Old admin account deleted")

    # Check if admin already exists
    admin = User.query.filter_by(email=admin_email).first()
    if admin:
        print("✓ Admin user already exists")
        print(f"  📧 Email: {admin_email}")
        print(f"  🔑 Password: admin@123")
    else:
        new_admin = User(
            id=str(uuid.uuid4()),
            name='Admin',
            email=admin_email,
            phone='9876543210',
            role='admin',
            is_verified=True
        )
        new_admin.set_password('admin@123')
        db.session.add(new_admin)
        db.session.commit()
        print("✓ Admin user created successfully!")
        print(f"  📧 Email: {admin_email}")
        print(f"  🔑 Password: admin@123")
