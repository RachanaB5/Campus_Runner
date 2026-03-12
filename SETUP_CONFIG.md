# Campus Runner - Setup & Configuration Guide

## 🚀 Quick Start

### Step 1: Install Dependencies

#### Backend
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend
```bash
npm install
```

### Step 2: Configure Environment Variables

Copy the `.env.example` file to `.env` in the backend directory:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- `JWT_SECRET_KEY`: Change this to a secure random string
- Email settings (optional but recommended for order confirmations)

### Step 3: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python app.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### Step 4: Access the Application

Open your browser and visit: **http://localhost:5173/**

---

## 📨 Email Configuration (Optional)

The application can send order confirmation emails. To enable:

### Using Gmail:
1. Enable 2-Step Verification on your Google account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Update `.env`:
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-specific-password
   ```

### Using AWS SES:
```
MAIL_SERVER=email-smtp.region.amazonaws.com
MAIL_PORT=587
MAIL_USERNAME=your-aws-smtp-username
MAIL_PASSWORD=your-aws-smtp-password
```

### Using SendGrid:
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

---

## 🗄️ Database

The application uses **SQLite** which is automatically initialized with sample data on first run.

To reset the database:
```bash
# Delete the database file
rm backend/instance/campusrunner.db

# Restart the backend - it will recreate with sample data
python backend/app.py
```

---

## 🔐 Security Notes

For production:
1. Change `JWT_SECRET_KEY` to a secure random string
2. Set `DEBUG=False` in `.env`
3. Use proper email service credentials
4. Enable HTTPS
5. Use a production database (PostgreSQL recommended)

---

## 📋 Features

- ✅ User Registration & Login
- ✅ Browse Food Menu with Categories
- ✅ Shopping Cart Management
- ✅ Advanced Checkout with Real-time Validation
- ✅ Order Confirmation (Email & In-App)
- ✅ Order Tracking
- ✅ Delivery Runner Mode
- ✅ Rewards Points System
- ✅ Professional Dark Mode Support

---

## 🆘 Troubleshooting

### Email Not Sending?
- Check your email credentials in `.env`
- Verify MAIL_USE_TLS setting (usually True for port 587)
- Check backend logs for error messages

### Port Already in Use?
```bash
# Kill the process using the port
lsof -ti:5000 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend
```

### Database Errors?
- Delete `backend/instance/campusrunner.db`
- Restart the backend to recreate the database

---

## 👥 User Roles

1. **Customer** - Browse menu, place orders, track delivery
2. **Runner** - Handle food delivery (Runner Mode)
3. **Admin** - Manage menu, orders, system settings

---

## 📞 Support

For issues, please check:
- Backend logs (in terminal window)
- Browser console (F12 → Console tab)
- Network tab for API errors (F12 → Network tab)
