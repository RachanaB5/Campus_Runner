# Order Tracking & Delivery System Implementation

## Overview
Complete order lifecycle tracking system with multi-stage workflow, OTP-based delivery verification, and real-time status management.

## ✅ Implementation Complete

### 1. **Database Models**

#### Order Model (`/backend/models/order.py`)
Enhanced with comprehensive tracking timestamps:
- `received_by_canteen_at` - When canteen receives the order
- `preparation_started_at` - When food preparation begins
- `ready_for_pickup_at` - When food is ready for delivery runner
- `picked_up_at` - When runner picks up the order
- `in_transit_at` - When order is in transit to customer
- `delivered_at` - When order is successfully delivered (set on OTP confirmation)

Status values progression:
```
pending → received → preparing → ready → picked_up → in_transit → awaiting_confirmation → delivered
```

#### OrderOTP Model (`/backend/models/otp.py`) - NEW
Secure OTP-based delivery verification:
- 6-digit random OTP generation
- 15-minute expiration time
- Verification tracking (`is_verified`, `verified_at`)
- Links to Order and Delivery models
- One OTP per delivery

**Key Methods:**
- `generate_otp()` - Creates random 6-digit code
- `create_for_order(order_id, delivery_id)` - Factory method with auto-expiration

---

## API Endpoints

### **Canteen Staff Endpoints** (Admin/Staff Role Required)

#### 1. Mark Order Received
```
POST /api/order/<order_id>/receive
Authorization: Bearer <token>

Response: {
  "message": "Order received by canteen",
  "order": { ...order details... }
}
```
**What it does:**
- Changes order status: pending → received
- Records `received_by_canteen_at` timestamp
- Allows staff to confirm order receipt from kitchen

#### 2. Start Preparation
```
POST /api/order/<order_id>/start-preparation
Authorization: Bearer <token>

Requirements: Order must be in 'received' status

Response: {
  "message": "Order preparation started",
  "order": { ...order details... }
}
```
**What it does:**
- Changes order status: received → preparing
- Records `preparation_started_at` timestamp
- Indicates kitchen has started working on order

#### 3. Mark Order Ready
```
POST /api/order/<order_id>/mark-ready
Authorization: Bearer <token>

Requirements: Order must be in 'preparing' status

Response: {
  "message": "Order marked as ready",
  "order": { ...order details... }
}
```
**What it does:**
- Changes order status: preparing → ready
- Records `ready_for_pickup_at` timestamp
- Makes order visible to runners for pickup

---

### **Runner Delivery Endpoints** (Runner Role Required)

#### 1. Get Available Orders
```
GET /api/runner/available-orders
Authorization: Bearer <token>

Response: {
  "available_orders": [
    {
      "id": "order-uuid",
      "order_number": "ORD-20260317-ABC1",
      "customer_name": "John Doe",
      "customer_phone": "9876543210",
      "items": [...],
      "total_amount": 450.00,
      "status": "ready",
      "ready_for_pickup_at": "2026-03-17T10:30:00"
    }
  ],
  "count": 5
}
```
**What it does:**
- Shows all orders ready for pickup
- Filters to only show unassigned orders
- Displays customer data for contactless verification

#### 2. Runner Picks Up Order
```
POST /api/runner/pickup-order/<order_id>
Authorization: Bearer <token>

Response: {
  "message": "Order picked up successfully",
  "order": { ...updated order... },
  "delivery": { ...delivery details... }
}
```
**What it does:**
- Runner claims the order
- Changes order status: ready → picked_up
- Records `picked_up_at` timestamp
- Creates Delivery record linking order to runner

#### 3. Mark In Transit
```
POST /api/runner/mark-in-transit/<order_id>
Authorization: Bearer <token>

Response: {
  "message": "Order marked as in transit",
  "order": { ...updated order... }
}
```
**What it does:**
- Changes order status: picked_up → in_transit
- Records `in_transit_at` timestamp
- Notifies customer via email that delivery is underway

#### 4. Deliver Order (Generate OTP)
```
POST /api/runner/deliver-order/<order_id>
Authorization: Bearer <token>

Response: {
  "message": "OTP sent to customer email",
  "order": { ...updated order... },
  "otp": "123456"  (for testing - not sent to customer)
}
```
**What it does:**
- Runner confirms arrival at delivery location
- Generates 6-digit OTP
- Sends OTP to customer's registered email address
- Changes order status: in_transit → awaiting_otp_verification
- Records email delivery attempt

#### 5. Confirm Delivery with OTP
```
POST /api/runner/confirm-delivery/<order_id>
Authorization: Bearer <token>
Content-Type: application/json

Body: {
  "otp": "123456"
}

Response: {
  "message": "Delivery confirmed successfully",
  "order": { ...updated order... }
}
```
**What it does:**
- Runner enters OTP provided by customer
- Validates OTP:
  - Is it correct?
  - Is it not expired (< 15 minutes)?
  - Not already used?
- Changes order status: awaiting_otp_verification → delivered
- Records `delivered_at` timestamp
- Marks OTP as verified with `verified_at` timestamp

---

## Complete Order Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE ORDER LIFECYCLE                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

1. CUSTOMER PLACES ORDER
   └─> Order created with status='pending', total_amount, items

2. CANTEEN RECEIVES
   └─> Staff: POST /api/order/<id>/receive
   └─> Status: pending → received
   └─> received_by_canteen_at timestamp recorded

3. KITCHEN PREPARES
   └─> Staff: POST /api/order/<id>/start-preparation
   └─> Status: received → preparing
   └─> preparation_started_at timestamp recorded
   └─> (Kitchen displays order on screen)

4. FOOD READY
   └─> Staff: POST /api/order/<id>/mark-ready
   └─> Status: preparing → ready
   └─> ready_for_pickup_at timestamp recorded
   └─> (Order available in runner app)

5. RUNNER CHECKS AVAILABLE
   └─> Runner: GET /api/runner/available-orders
   └─> Sees list of ready orders with customer details

6. RUNNER PICKS UP
   └─> Runner: POST /api/runner/pickup-order/<id>
   └─> Status: ready → picked_up
   └─> picked_up_at timestamp recorded
   └─> Delivery record created

7. RUNNER IN TRANSIT
   └─> Runner: POST /api/runner/mark-in-transit/<id>
   └─> Status: picked_up → in_transit
   └─> in_transit_at timestamp recorded
   └─> (Customer email: "Your order is on the way!")

8. RUNNER ARRIVES
   └─> Runner: POST /api/runner/deliver-order/<id>
   └─> Generates 6-digit OTP (e.g., "547382")
   └─> Sends OTP to customer@email.com
   └─> Status: in_transit → awaiting_otp_verification
   └─> Order now awaits OTP verification

9. DELIVERY CONFIRMATION
   └─> Customer receives email with OTP: "547382"
   └─> Customer shares OTP with runner (or runner enters it)
   └─> Runner: POST /api/runner/confirm-delivery/<id>
   └─> Body: {"otp": "547382"}
   └─> OTP validated (correct, not expired, not reused)
   └─> Status: awaiting_otp_verification → delivered
   └─> delivered_at timestamp recorded
   └─> Order completed ✓

┌─────────────────────────────────────────────────────────────────────────────────┐
│                         TRACKING DATA AVAILABLE                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

When you GET /api/order/<id>, response includes all timestamps:

{
  "id": "order-uuid",
  "status": "delivered",
  "customer_name": "John Doe",
  "total_amount": 450.00,
  "items": [...],
  
  // TRACKING TIMELINE
  "received_by_canteen_at": "2026-03-17T10:00:00",    (5 minutes ago)
  "preparation_started_at": "2026-03-17T10:05:00",    (just started)
  "ready_for_pickup_at": "2026-03-17T10:22:00",       (ready!)
  "picked_up_at": "2026-03-17T10:25:00",              (runner here)
  "in_transit_at": "2026-03-17T10:26:00",             (out for delivery)
  "delivered_at": "2026-03-17T10:35:00",              (delivered!)
  
  // DELIVERY INFO
  "delivery": {
    "runner_name": "Rahul Kumar",
    "runner_phone": "9876543210",
    "status": "delivered"
  }
}
```

---

## Security Features

### OTP Verification
1. **One-Time Use**: Each OTP can only be used once
2. **Time-Limited**: OTPs expire after 15 minutes
3. **Validation**: Checked for correctness, expiration, and reuse
4. **Tracking**: Verified timestamp recorded for audit trail

### Role-Based Access Control
- **Canteen Staff**: Can only mark order progression (receive → preparing → ready)
- **Runners**: Can only pick up orders, mark status, and verify delivery
- **Admin**: Can do everything
- **Customers**: Can view their order tracking

### Data Validation
- Order must be in correct status before advancing
- Runner must exist in database before picking up orders
- OTP must exist and be valid before confirmation

---

## Database Schema Updates

### Order Table (Modified)
```sql
- received_by_canteen_at: DATETIME (nullable)
- preparation_started_at: DATETIME (nullable)
- ready_for_pickup_at: DATETIME (nullable)
- picked_up_at: DATETIME (nullable)
- in_transit_at: DATETIME (nullable)
- delivered_at: DATETIME (nullable)
```

### OrderOTP Table (New)
```sql
- id: UUID (primary key)
- order_id: UUID (foreign key → Order)
- delivery_id: UUID (foreign key → Delivery)
- otp: VARCHAR(6) (6-digit code)
- is_verified: BOOLEAN (default: False)
- verified_at: DATETIME (nullable)
- expires_at: DATETIME (15 min from creation)
- created_at: DATETIME (auto-set)
```

---

## Testing the Workflow

### 1. Get Authentication Token
```bash
curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@rvu.edu.in",
    "password": "admin@123"
  }'
```

Response will include `access_token` - use this in Authorization header.

### 2. Create an Order (as customer)
```bash
# Register customer first
curl -X POST "http://localhost:5000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Customer",
    "email": "customer@example.com",
    "password": "password123",
    "phone": "9876543210",
    "role": "customer"
  }'

# Login as customer
curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123"
  }'

# Create order with customer token
curl -X POST "http://localhost:5000/api/order/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <CUSTOMER_TOKEN>" \
  -d '{
    "items": [{"food_id": "1", "quantity": 2}],
    "delivery_address": "123 Main St",
    "phone": "9876543210"
  }'
```

### 3. Canteen Staff Processes Order
```bash
# Using admin/staff token
STAFF_TOKEN="<admin token>"
ORDER_ID="<from create response>"

# Receive order
curl -X POST "http://localhost:5000/api/order/$ORDER_ID/receive" \
  -H "Authorization: Bearer $STAFF_TOKEN"

# Start preparation
curl -X POST "http://localhost:5000/api/order/$ORDER_ID/start-preparation" \
  -H "Authorization: Bearer $STAFF_TOKEN"

# Mark ready
curl -X POST "http://localhost:5000/api/order/$ORDER_ID/mark-ready" \
  -H "Authorization: Bearer $STAFF_TOKEN"
```

### 4. Runner Picks Up
```bash
# Using admin/runner token
RUNNER_TOKEN="<staff/runner token>"

# Get available orders
curl -X GET "http://localhost:5000/api/runner/available-orders" \
  -H "Authorization: Bearer $RUNNER_TOKEN"

# Pick up order
curl -X POST "http://localhost:5000/api/runner/pickup-order/$ORDER_ID" \
  -H "Authorization: Bearer $RUNNER_TOKEN"

# Mark in transit
curl -X POST "http://localhost:5000/api/runner/mark-in-transit/$ORDER_ID" \
  -H "Authorization: Bearer $RUNNER_TOKEN"

# Deliver (OTP generated and emailed)
curl -X POST "http://localhost:5000/api/runner/deliver-order/$ORDER_ID" \
  -H "Authorization: Bearer $RUNNER_TOKEN"

# Confirm delivery with OTP
curl -X POST "http://localhost:5000/api/runner/confirm-delivery/$ORDER_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RUNNER_TOKEN" \
  -d '{"otp": "123456"}'
```

---

## Email Notifications

### OTP Delivery Email
When `POST /api/runner/deliver-order/<order_id>` is called:
- **To:** Customer's registered email address
- **Subject:** "Your Campus Runner Order Delivery OTP"
- **Body:** Contains 6-digit OTP code and instructions
- **Server:** Sent via Firebase/Gmail SMTP service

### Order Status Emails (Future)
- "Order received by canteen"
- "Your order is being prepared"
- "Order ready for delivery!"
- "Order out for delivery - runner on the way"
- "Delivery confirmed!"

---

## Files Modified

1. **`/backend/models/order.py`**
   - Added 6 tracking timestamp fields
   - Updated `to_dict()` to include tracking data

2. **`/backend/models/otp.py`** (NEW)
   - OrderOTP model with OTP generation and validation

3. **`/backend/models/__init__.py`**
   - Added OrderOTP import and export

4. **`/backend/routes/order_routes.py`**
   - Added `/receive` endpoint
   - Added `/start-preparation` endpoint
   - Added `/mark-ready` endpoint

5. **`/backend/routes/runner_routes.py`**
   - Added `/available-orders` endpoint
   - Added `/pickup-order/<id>` endpoint
   - Added `/mark-in-transit/<id>` endpoint
   - Added `/deliver-order/<id>` endpoint
   - Added `/confirm-delivery/<id>` endpoint

---

## Next Steps (Frontend Implementation)

### Components Needed
1. **Canteen Staff Dashboard**
   - Display pending orders
   - Quick buttons: "Received" → "Preparing" → "Ready"
   - Order details and items

2. **Runner Dashboard**
   - Live list of available orders with refresh
   - Pickup button → In Transit button → Deliver button
   - Current order details
   - GPS location sharing

3. **Customer Order Tracking**
   - Order status timeline (visual)
   - Current stage indication
   - Runner details when assigned
   - OTP entry screen when delivery arrives

4. **Real-Time Updates**
   - WebSocket connections for live status changes
   - Toast notifications when status updates
   - Live runner location on map

---

## Error Handling

All endpoints include:
- ✅ JWT authentication validation
- ✅ Database transaction rollback on errors
- ✅ Detailed error messages
- ✅ Proper HTTP status codes
- ✅ Logging with ✅ (success) or ❌ (failure) indicators

---

## Summary

**Complete order tracking system with:**
- ✅ Multi-stage order workflow
- ✅ OTP-based secure delivery verification
- ✅ Comprehensive audit trail with timestamps
- ✅ Role-based access control
- ✅ Real-time status management
- ✅ Email notifications for OTPs
- ✅ Full error handling and validation

**Ready for:** Customer order tracking UI, Runner delivery app, Admin dashboard integration
