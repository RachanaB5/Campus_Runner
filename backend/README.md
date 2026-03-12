# CampusRunner Backend - Setup & Installation Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ ([Download](https://nodejs.org))
- MongoDB 4.4+ ([Download](https://www.mongodb.com/try/download/community) or use MongoDB Atlas)
- npm or yarn

### Installation Steps

1. **Clone/Navigate to project**
```bash
cd backend
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
NODE_ENV=development
PORT=5000
MONGODB_URI=mongodb://localhost:27017/campusrunner

JWT_SECRET=your-super-secret-key-change-in-production
JWT_EXPIRE=7d

# Razorpay (optional - for testing, use test keys)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Email (Gmail example)
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Firebase (optional - for push notifications)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-email@project.iam.gserviceaccount.com

FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:5000
```

4. **Start development server**
```bash
npm run dev
```

Server will start on `http://localhost:5000`

---

## 🗄️ Database Setup

### Local MongoDB
```bash
# macOS (using Homebrew)
brew install mongodb-community
brew services start mongodb-community

# Verify connection
mongosh
```

### MongoDB Atlas (Cloud)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create cluster
3. Get connection string
4. Update `MONGODB_URI` in `.env`

---

## 📝 Seeding Test Data

```bash
npm run seed
```

This creates:
- 10 test users (students, runners, staff, admin)
- 20 food items across different categories
- Sample orders and tokens

---

## 🔑 Getting API Keys

### Razorpay
1. Sign up at [Razorpay](https://razorpay.com)
2. Go to Settings → API Keys
3. Copy test keys (for development)
4. Add to `.env`

### Firebase
1. Create project at [Firebase Console](https://console.firebase.google.com)
2. Go to Project Settings
3. Generate new private key
4. Add credentials to `.env`

### Email (Gmail)
1. Enable 2-Step Verification on Google Account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate app-specific password
4. Add to `.env`

---

## 📚 API Testing

### Using Postman
1. Import API collection from `postman_collection.json`
2. Set environment variables (JWT token, base URL)
3. Test endpoints

### Using cURL
```bash
# Health check
curl http://localhost:5000/health

# Signup
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@rvu.edu.in",
    "phone": "9876543210",
    "password": "test123",
    "universityId": "RVU001"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@rvu.edu.in",
    "password": "test123"
  }'

# Get menu
curl http://localhost:5000/api/menu
```

---

## 🗂️ Project Structure

```
src/
├── config/              # Database & configuration
├── middleware/          # Authentication & validation
├── models/             # MongoDB schemas
├── controllers/        # Business logic
├── routes/            # API endpoints
├── services/          # Utilities & helpers
│   ├── paymentService.ts
│   ├── rewardService.ts
│   ├── notificationService.ts
│   └── runnerMatchingService.ts
├── utils/
│   ├── helpers.ts      # Utility functions
│   └── email.ts        # Email templates
└── server.ts           # Main Express app
```

---

## ✅ Key Features Implemented

### Authentication
- [x] JWT token-based auth
- [x] User signup/login
- [x] Role-based access control
- [ ] OAuth2 (Google login) - TODO

### Menu Management
- [x] Browse food items
- [x] Category filtering
- [x] Admin CRUD operations
- [x] Counter management

### Orders
- [x] Create orders
- [x] Track order status
- [x] Digital token generation
- [x] Queue management (FCFS)
- [x] Order cancellation & ratings

### Runner System
- [x] Runner registration
- [x] Availability toggle
- [x] Delivery acceptance
- [x] GPS tracking (mock)
- [x] Earnings tracking
- [x] Smart runner matching

### Rewards
- [x] Points earning system
- [x] Reward redemption
- [x] Transaction history
- [x] Peak hour bonuses

### Payments
- [x] Razorpay integration
- [x] Payment verification
- [x] Refund handling

### Staff/Admin
- [x] Order management dashboard
- [x] Queue display
- [x] Analytics & reports
- [x] User management

### Notifications
- [x] Email notifications
- [x] Push notifications (Firebase)
- [x] In-app notifications (ready)

---

## 🧪 Running Tests

```bash
npm test
```

Currently no tests configured. To set up:

1. Install Jest
```bash
npm install --save-dev jest @types/jest ts-jest
```

2. Create `jest.config.js`:
```js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
};
```

3. Add test scripts to `package.json`

---

## 🚢 Production Deployment

### Build for Production
```bash
npm run build
npm start
```

### Environment Variables (Production)
```env
NODE_ENV=production
JWT_SECRET=your-very-secure-secret-key
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/campusrunner
```

### Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist

EXPOSE 5000
CMD ["node", "dist/server.js"]
```

Build & run:
```bash
docker build -t campusrunner-backend .
docker run -p 5000:5000 --env-file .env campusrunner-backend
```

### Cloud Deployment Options
- Railway.app
- Render
- Heroku
- AWS Lambda
- Google Cloud Run

---

## 🐛 Troubleshooting

### MongoDB Connection Error
```
Error: connect ECONNREFUSED
```
Solution: Start MongoDB service
```bash
mongosh  # Verify connection
```

### Port Already in Use
```
Error: listen EADDRINUSE: address already in use :::5000
```
Solution: Change PORT in `.env` or kill existing process

### JWT Token Invalid
- Ensure `JWT_SECRET` is set in `.env`
- Check token format in request header
- Token might be expired

### Razorpay Test Mode
- Use test API keys from Razorpay dashboard
- Test card: `4111 1111 1111 1111`
- Any future date for expiry

---

## 📚 Additional Resources

- [Express.js Docs](https://expressjs.com)
- [MongoDB Docs](https://docs.mongodb.com)
- [Razorpay API](https://razorpay.com/docs)
- [Firebase Messaging](https://firebase.google.com/docs/cloud-messaging)
- [JWT Auth](https://jwt.io)

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/xyz`
2. Commit changes: `git commit -m 'Add xyz'`
3. Push to branch: `git push origin feature/xyz`
4. Open Pull Request

---

## 📞 Support

For issues or questions:
- Post in issues section
- Email: dev@campusrunner.com

---

## 📄 License

MIT License - See LICENSE file for details
