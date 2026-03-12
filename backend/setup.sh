#!/bin/bash

# CampusRunner Backend - Quick Setup Script
# Run this script to set up the backend development environment

echo "🚀 CampusRunner Backend Setup"
echo "=============================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ npm install failed"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Check MongoDB
echo "🗄️ Checking MongoDB..."
if ! command -v mongosh &> /dev/null; then
    echo "⚠️  MongoDB not found. Install from https://www.mongodb.com/try/download"
    echo "   Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas"
fi

echo ""

# Create .env file
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "✅ .env created. Please update with your credentials:"
    echo "   - MONGODB_URI"
    echo "   - JWT_SECRET"
    echo "   - RAZORPAY_* keys"
    echo "   - Email credentials"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Start MongoDB: brew services start mongodb-community (macOS)"
echo "3. Run development server: npm run dev"
echo "4. API will be available at http://localhost:5000"
echo ""
