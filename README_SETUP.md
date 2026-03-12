# CampusCanteen - Food Ordering & Management System

A fully-functional **Canteen Food Management and Ordering System** with:
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Python Flask + SQLAlchemy + SQLite
- **Features**: User authentication, menu browsing, cart management, order tracking, and reward points

## Project Structure

```
project/
├── src/                          # Frontend (React)
│   ├── app/
│   │   ├── components/           # Reusable components (Header, FoodCard, etc.)
│   │   ├── pages/                # Page components (Home, Cart, Orders, etc.)
│   │   ├── context/              # Context providers (Auth, Cart)
│   │   ├── services/             # API services
│   │   └── data/                 # Mock data
│   ├── styles/                   # CSS & Tailwind styles
│   ├── main.tsx                  # App entry point
│   └── assets/                   # Images & static files
│
├── backend/                      # Python Flask API
│   ├── app.py                    # Flask application entry
│   ├── models/                   # Database models
│   │   ├── user.py              # User model
│   │   ├── food.py              # Food menu items
│   │   ├── order.py             # Orders
│   │   ├── cart.py              # Shopping cart
│   │   ├── delivery.py          # Deliveries
│   │   ├── runner.py            # Delivery runners
│   │   ├── reward_points.py     # Reward system
│   │   └── token.py             # Auth tokens
│   ├── routes/                   # API endpoints
│   │   ├── auth_routes.py       # Authentication
│   │   ├── menu_routes.py       # Menu/Food endpoints
│   │   ├── cart_routes.py       # Cart operations
│   │   ├── order_routes.py      # Order management
│   │   ├── runner_routes.py     # Runner operations
│   │   └── staff_admin_routes.py # Admin functions
│   ├── services/                 # Business logic
│   │   ├── notificationService.ts
│   │   ├── paymentService.ts
│   │   └── rewardService.ts
│   ├── requirements.txt           # Python dependencies
│   ├── init_db.py                # Database initialization
│   ├── run.sh                    # Run backend server
│   └── setup.sh                  # Setup script
│
├── package.json                  # Frontend dependencies
├── tsconfig.json                 # TypeScript config
├── vite.config.ts               # Vite configuration
├── postcss.config.mjs           # PostCSS config
└── README.md                     # This file
```

## Quick Start

### Prerequisites
- Node.js (v18+)
- Python (v3.8+)
- npm or yarn

### 1. Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```
Frontend runs on: `http://localhost:5173`

### 2. Backend Setup

```bash
# Create Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate    # On macOS/Linux
# or
.venv\Scripts\activate       # On Windows

# Install Python dependencies
pip install -r backend/requirements.txt

# Initialize database with sample data
python3 backend/init_db.py

# Start Flask server
python3 backend/app.py
# or
bash backend/run.sh
```
Backend runs on: `http://localhost:5000`

## Features

### 👤 User Features
- **Authentication**: Sign up, login with email/password
- **Menu Browsing**: View all canteen items with categories and filters
- **Shopping Cart**: Add/remove items, update quantities
- **Order Management**: Place orders, track delivery status
- **Reward System**: Earn points with each order
- **Profile Management**: Update personal information

### 🏃 Runner Features
- **Availability Status**: Toggle availability for deliveries
- **Order Tracking**: Real-time delivery updates
- **Location Updates**: Update current location
- **Rating System**: Get rated by customers

### 👨‍💼 Admin/Staff Features
- **Dashboard**: View sales, orders, and statistics
- **Food Management**: Add, edit, delete menu items
- **Order Management**: Assign runners, mark items ready
- **User Management**: Manage customer and runner accounts
- **Reports**: Generate sales and analytics reports

## API Endpoints

### Authentication
```
POST   /api/auth/register          - Register new user
POST   /api/auth/login             - Login
GET    /api/auth/me                - Get current user
PUT    /api/auth/update-profile    - Update profile
POST   /api/auth/logout            - Logout
```

### Menu/Food
```
GET    /api/menu/all               - Get all food items
GET    /api/menu/category/:cat     - Get items by category
GET    /api/menu/:id               - Get food details
POST   /api/menu/add               - Add food (admin)
PUT    /api/menu/:id               - Update food (admin)
DELETE /api/menu/:id               - Delete food (admin)
```

### Cart
```
GET    /api/cart/get               - Get user's cart
POST   /api/cart/add               - Add item to cart
PUT    /api/cart/item/:id          - Update cart item
DELETE /api/cart/item/:id          - Remove from cart
DELETE /api/cart/clear             - Clear entire cart
```

### Orders
```
POST   /api/order/create           - Create new order
GET    /api/order/my-orders        - Get user's orders
GET    /api/order/:id              - Get order details
POST   /api/order/:id/cancel       - Cancel order
POST   /api/order/:id/confirm      - Confirm order
```

### Runner
```
GET    /api/runner/available       - Get available deliveries
POST   /api/runner/accept/:id      - Accept delivery
GET    /api/runner/my-deliveries   - Get runner's deliveries
POST   /api/runner/delivery/:id/update-status - Update delivery status
```

### Admin
```
GET    /api/admin/dashboard-stats  - Dashboard statistics
GET    /api/admin/orders           - All orders (with filters)
GET    /api/admin/users            - All users
GET    /api/admin/foods/inventory  - Food inventory
```

## Database Models

### User
- id, name, email, phone, password_hash, role, profile_image, wallet_balance, is_verified

### Food
- id, name, description, price, category, image_url, prep_time, available, rating, review_count

### Order
- id, customer_id, total_amount, delivery_address, status, items, created_at, updated_at

### Cart
- id, user_id, items, total_price, created_at, updated_at

### Delivery/Runner
- Tracking delivery status and runner assignments

### RewardPoints
- Track user points, redemptions, transactions

## Technology Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **Lucide Icons** - Icons
- **Radix UI** - Component library

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-CORS** - Cross-origin requests
- **Flask-JWT** - Authentication
- **SQLite** - Database

## Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///campuscanteen.db
JWT_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_PORT=5000
```

## Running the Application

### Development Mode

Terminal 1 (Frontend):
```bash
npm run dev
```

Terminal 2 (Backend):
```bash
source .venv/bin/activate
python3 backend/app.py
```

Visit: `http://localhost:5173`

### Production Build

```bash
# Build frontend
npm run build

# Run backend in production
python3 backend/app.py
```

## Key Features Demonstration

### 1. Browse Menu
- Visit home page and browse all food items
- Filter by category
- View item details with images and ratings

### 2. Add to Cart
- Click "Add to Cart" on any item
- Adjust quantities in cart
- View cart total

### 3. Place Order
- Checkout with items from cart
- Enter delivery address
- Process payment
- Track order status in real-time

### 4. Reward Points
- Earn points with every purchase
- View points in profile
- Redeem for discounts

## Error Handling

The application includes comprehensive error handling:
- Input validation
- Authentication errors
- Network errors with user-friendly messages
- Database transaction handling
- Session management

## Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt for secure password storage
- **CORS Protection**: Configure allowed origins
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **Role-Based Access**: Different permissions for users, runners, and admins

## Testing

To test the API endpoints, you can use:
- **Postman**: Import API documentation
- **cURL**: Command-line requests
- **REST Client Extensions**: VS Code extensions

Example:
```bash
# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@rv.edu.in","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@rv.edu.in","password":"password123"}'

# Get menu
curl http://localhost:5000/api/menu/all
```

## Troubleshooting

### Frontend Issues
- Check Node.js version: `node --version` (should be v18+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Vite port: Default is 5173, change in vite.config.ts

### Backend Issues
- Check Python version: `python3 --version` (should be 3.8+)
- Verify virtual environment: `which python` (should show .venv path)
- Check Flask port availability: `lsof -i :5000`
- Reset database: `rm instance/campuscanteen.db && python3 backend/init_db.py`

## File Manifest

See `FILE_MANIFEST.md` for detailed file descriptions.

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is proprietary and for educational purposes.

## Support

For issues or questions:
1. Check logs and error messages
2. Review API documentation
3. Check database setup
4. Verify environment variables

---

**Happy Ordering! 🍔🍕**
