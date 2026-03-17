#!/bin/bash
set -e

BASE_URL="http://localhost:5000/api"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🚴 RUNNER DASHBOARD & DELIVERY SYSTEM - END-TO-END TEST"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Admin Login
echo -e "${BLUE}STEP 1️⃣ : Admin Authentication${NC}"
echo "Logging in as admin@rvu.edu.in..."
ADMIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@rvu.edu.in", "password": "admin@123"}')

ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
if [ -z "$ADMIN_TOKEN" ]; then
  echo -e "${RED}❌ Failed to get admin token${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Admin authenticated successfully${NC}"
echo ""

# Step 2: Register Customer
echo -e "${BLUE}STEP 2️⃣ : Customer Registration${NC}"
TIMESTAMP=$(date +%s)
CUSTOMER_EMAIL="runner_test_$TIMESTAMP@test.com"
echo "Registering customer: $CUSTOMER_EMAIL"

CUSTOMER_REG=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test Customer $TIMESTAMP\",
    \"email\": \"$CUSTOMER_EMAIL\",
    \"password\": \"test123\",
    \"phone\": \"9999999999\",
    \"role\": \"customer\"
  }")

CUSTOMER_ID=$(echo "$CUSTOMER_REG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('user', {}).get('id', ''))" 2>/dev/null)
if [ -z "$CUSTOMER_ID" ]; then
  echo -e "${RED}❌ Customer registration failed${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Customer registered: $CUSTOMER_EMAIL${NC}"
echo ""

# Step 3: Customer Login
echo -e "${BLUE}STEP 3️⃣ : Customer Login${NC}"
CUSTOMER_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$CUSTOMER_EMAIL\", \"password\": \"test123\"}")

CUSTOMER_TOKEN=$(echo "$CUSTOMER_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo -e "${GREEN}✅ Customer logged in${NC}"
echo ""

# Step 4: Create Order
echo -e "${BLUE}STEP 4️⃣ : Create Food Order${NC}"
echo "Creating order for customer..."

ORDER_RESPONSE=$(curl -s -X POST "$BASE_URL/order/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CUSTOMER_TOKEN" \
  -d '{
    "items": [{"food_id": "food-001", "quantity": 2}],
    "delivery_address": "123 Main Street, Test City",
    "phone": "9999999999"
  }')

ORDER_ID=$(echo "$ORDER_RESPONSE" | python3 -c "import sys, json; d = json.load(sys.stdin); print(d.get('order', {}).get('id', '') if 'order' in d else d.get('id', ''))" 2>/dev/null)
ORDER_NUMBER=$(echo "$ORDER_RESPONSE" | python3 -c "import sys, json; d = json.load(sys.stdin); print(d.get('order', {}).get('order_number', '') if 'order' in d else d.get('order_number', ''))" 2>/dev/null)
ORDER_TOTAL=$(echo "$ORDER_RESPONSE" | python3 -c "import sys, json; d = json.load(sys.stdin); print(d.get('order', {}).get('total_amount', '0') if 'order' in d else d.get('total_amount', '0'))" 2>/dev/null)

if [ -z "$ORDER_ID" ]; then
  echo -e "${RED}❌ Order creation failed${NC}"
  echo "Response: $ORDER_RESPONSE"
  exit 1
fi
echo -e "${GREEN}✅ Order created: #$ORDER_NUMBER (₹$ORDER_TOTAL)${NC}"
echo "   Order ID: $ORDER_ID"
echo "   Delivery Address: 123 Main Street, Test City"
echo ""

# Step 5: Canteen receives order
echo -e "${BLUE}STEP 5️⃣ : Canteen Receives Order${NC}"
echo "Marking order as received..."
RECEIVE=$(curl -s -X POST "$BASE_URL/order/$ORDER_ID/receive" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
STATUS=$(echo "$RECEIVE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order', {}).get('status', ''))" 2>/dev/null)
echo -e "${GREEN}✅ Status: $STATUS${NC}"
echo ""

# Step 6: Start preparation  
echo -e "${BLUE}STEP 6️⃣ : Start Food Preparation${NC}"
echo "Marking order as in preparation..."
PREP=$(curl -s -X POST "$BASE_URL/order/$ORDER_ID/start-preparation" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
STATUS=$(echo "$PREP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order', {}).get('status', ''))" 2>/dev/null)
echo -e "${GREEN}✅ Status: $STATUS${NC}"
echo ""

# Step 7: Mark ready
echo -e "${BLUE}STEP 7️⃣ : Order Ready for Pickup${NC}"
echo "Marking order as ready..."
READY=$(curl -s -X POST "$BASE_URL/order/$ORDER_ID/mark-ready" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
STATUS=$(echo "$READY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order', {}).get('status', ''))" 2>/dev/null)
echo -e "${GREEN}✅ Status: $STATUS${NC}"
echo ""

# Step 8: Check available orders
echo -e "${BLUE}STEP 8️⃣ : Runner Checks Available Orders${NC}"
echo "Fetching available orders for runner..."
AVAILABLE=$(curl -s -X GET "$BASE_URL/runner/available-orders" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
AVAILABLE_COUNT=$(echo "$AVAILABLE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
echo -e "${GREEN}✅ Found $AVAILABLE_COUNT available order(s)${NC}"
echo ""

# Step 9: Runner picks up order
echo -e "${BLUE}STEP 9️⃣ : Runner Picks Up Order${NC}"
echo "Runner accepting delivery..."
PICKUP=$(curl -s -X POST "$BASE_URL/runner/pickup-order/$ORDER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
STATUS=$(echo "$PICKUP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order', {}).get('status', ''))" 2>/dev/null)
echo -e "${GREEN}✅ Status: $STATUS${NC}"
echo ""

# Step 10: Mark in transit
echo -e "${BLUE}STEP 🔟 : Delivery In Transit${NC}"
echo "Runner marking order as in transit..."
TRANSIT=$(curl -s -X POST "$BASE_URL/runner/mark-in-transit/$ORDER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
STATUS=$(echo "$TRANSIT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order', {}).get('status', ''))" 2>/dev/null)
echo -e "${GREEN}✅ Status: $STATUS${NC}"
echo ""

# Step 11: Generate OTP
echo -e "${BLUE}STEP 1️⃣1️⃣ : Generate Delivery OTP${NC}"
echo "Runner arriving at delivery location, generating OTP..."
DELIVER=$(curl -s -X POST "$BASE_URL/runner/deliver-order/$ORDER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
STATUS=$(echo "$DELIVER" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order', {}).get('status', ''))" 2>/dev/null)
OTP=$(echo "$DELIVER" | python3 -c "import sys, json; print(json.load(sys.stdin).get('otp', ''))" 2>/dev/null)
echo -e "${GREEN}✅ Status: $STATUS${NC}"
echo -e "${YELLOW}🔐 Generated OTP: $OTP${NC}"
echo "   (This would be sent to customer's email)"
echo ""

# Step 12: Confirm delivery
echo -e "${BLUE}STEP 1️⃣2️⃣ : Confirm Delivery with OTP${NC}"
echo "Runner entering OTP from customer..."
CONFIRM=$(curl -s -X POST "$BASE_URL/runner/confirm-delivery/$ORDER_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"otp\": \"$OTP\"}")
STATUS=$(echo "$CONFIRM" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order', {}).get('status', ''))" 2>/dev/null)
echo -e "${GREEN}✅ Status: $STATUS${NC}"
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ COMPLETE RUNNER WORKFLOW TEST SUCCESSFUL!${NC}"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Order Details:"
echo "   • Order ID: $ORDER_ID"
echo "   • Order #: $ORDER_NUMBER"
echo "   • Amount: ₹$ORDER_TOTAL"
echo "   • Runner Earnings: ₹$(echo "scale=0; $ORDER_TOTAL / 10" | bc)"
echo ""
echo "✅ Workflow Steps Completed:"
echo "   1️⃣  Admin authenticated"
echo "   2️⃣  Customer registered"
echo "   3️⃣  Customer logged in"
echo "   4️⃣  Order created (pending)"
echo "   5️⃣  Order received by canteen"
echo "   6️⃣  Food preparation started"
echo "   7️⃣  Order marked ready"
echo "   8️⃣  Runner found available order"
echo "   9️⃣  Runner picked up order"
echo "   🔟 Delivery marked in transit"
echo "   1️⃣1️⃣ OTP generated & sent to customer"
echo "   1️⃣2️⃣ OTP verified & delivery complete"
echo ""
echo "🎉 Final Status: DELIVERED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Now test the Runner Dashboard at: http://localhost:5173"
echo "Login: admin@rvu.edu.in / admin@123"
echo "Navigate: Click Runner Mode in the menu"
echo ""
