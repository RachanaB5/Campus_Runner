# Quick Start Guide - CampusCanteen

Get up and running in **2 minutes**! 🚀

## Prerequisites Check
```bash
node --version    # Should be v18+
python3 --version # Should be 3.8+
```

## Run in Two Terminal Windows

### Terminal 1: Backend (Flask API)
```bash
cd "/Users/rachanabhaskargowda/Desktop/Food Ordering Website Design"
source .venv/bin/activate
python3 backend/app.py
```

✅ When you see: `Running on http://127.0.0.1:5000`

### Terminal 2: Frontend (React)
```bash
cd "/Users/rachanabhaskargowda/Desktop/Food Ordering Website Design"
npm run dev
```

✅ When you see: `Local: http://localhost:5173/`

## Open Browser
Visit: **http://localhost:5173/**

---

## First Time Setup (Optional - Already Done!)

If you need to reinitialize the database with food items:

```bash
cd "/Users/rachanabhaskargowda/Desktop/Food Ordering Website Design"
source .venv/bin/activate
python3 backend/init_db.py
```

---

## Test the App

### 1. Sign Up
- Click "Login" button → "Sign Up"
- Enter name, email, password
- Click Register

### 2. Browse Menu
- You're on Home page with all food items
- See 14 dishes from the canteen
- Click on items to see details

### 3. Add to Cart
- Click "Add" button on any item
- See success message
- Check cart count in header

### 4. View Cart
- Click shopping cart icon
- See all items, adjust quantities
- Total price at bottom

### 5. Place Order
- Click "Checkout" in cart
- Enter delivery address
- Click "Place Order"

### 6. Track Orders
- Click "Orders" in navigation
- See all your orders with status

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "Module not found" | Run: `npm install --legacy-peer-deps` |
| Port 5000/5173 in use | Kill the process or use different port |
| Database error | Run: `python3 backend/init_db.py` |
| CORS error | Backend must run on 5000, frontend on 5173 |

---

## File Locations

| Component | Location |
|-----------|----------|
| Frontend | `/src/` |
| Backend | `/backend/` |
| Database | `/backend/instance/campuscanteen.db` |
| API Base URL | `http://localhost:5000/api` |

---

## Menu Items Included

14 ready-to-order items:
- 🍗 Main Courses (Butter Chicken, Biryani, Paneer Tikka)
- 🍚 Rice Dishes (Veg & Chicken Fried Rice)
- 🥬 Vegetarian (Dal, Aloo Gobi)
- 🥟 Appetizers (Samosa)
- 🍞 Bread (Naan, Roti)
- 🥤 Beverages (Coke, Lassi)
- 🍰 Desserts (Gulab Jamun, Ice Cream)

---

## Architecture

```
Browser (http://localhost:5173)
         ↓
    React App
         ↓  (HTTP Requests)
    Flask API (http://localhost:5000)
         ↓
    SQLite Database (14 items)
```

---

## Features Included

✅ User Registration & Login  
✅ Browse Food Menu  
✅ Shopping Cart  
✅ Order Placement  
✅ Order Tracking  
✅ User Profile  
✅ Admin Dashboard  
✅ Reward Points  

---

**Ready? Open your browser and visit: http://localhost:5173/**

For detailed docs, see: `IMPLEMENTATION_GUIDE.md` or `README_SETUP.md`
