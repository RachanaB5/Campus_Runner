# Campus Runner Architecture Diagrams

This document contains Mermaid diagrams for core backend domain modeling and request flows.

## 1) Domain Class Diagram (Backend Models)

```mermaid
classDiagram
    class User {
      +id: string
      +name: string
      +email: string
      +phone: string
      +role: string
      +wallet_balance: float
      +is_verified: bool
    }

    class Runner {
      +id: string
      +user_id: string
      +vehicle_type: string
      +status: string
      +is_available: bool
    }

    class Cart {
      +id: string
      +user_id: string
      +total_price: float
      +item_count: int
    }

    class CartItem {
      +id: string
      +cart_id: string
      +food_id: string
      +quantity: int
      +price: float
      +customizations: text
    }

    class Food {
      +id: string
      +name: string
      +category: string
      +price: float
      +available: bool
      +rating: float
      +review_count: int
    }

    class Checkout {
      +id: string
      +customer_id: string
      +order_id: string
      +delivery_address: text
      +customer_phone: string
      +payment_method: string
      +subtotal: float
      +tax_amount: float
      +delivery_fee: float
      +final_total: float
      +checkout_status: string
      +validate_all()
    }

    class Order {
      +id: string
      +customer_id: string
      +order_number: string
      +status: string
      +payment_status: string
      +payment_method: string
      +total_amount: float
      +delivery_fee: float
      +estimated_delivery_time: datetime
    }

    class OrderItem {
      +id: string
      +order_id: string
      +food_id: string
      +quantity: int
      +unit_price: float
      +total_price: float
    }

    class Delivery {
      +id: string
      +order_id: string
      +runner_id: string
      +status: string
      +estimated_time_minutes: int
      +delivered_at: datetime
    }

    class OrderOTP {
      +id: string
      +order_id: string
      +delivery_id: string
      +otp_type: string
      +otp: string
      +is_used: bool
    }

    class Payment {
      +id: string
      +order_id: string
      +user_id: string
      +method: string
      +amount: int
      +status: string
    }

    class Review {
      +id: string
      +user_id: string
      +food_id: string
      +order_id: string
      +rating: int
      +comment: text
    }

    class Notification {
      +id: string
      +user_id: string
      +title: string
      +body: text
      +type: string
      +is_read: bool
    }

    class RewardPoints {
      +id: string
      +user_id: string
      +points_balance: int
      +tier: string
    }

    class RewardTransaction {
      +id: string
      +reward_points_id: string
      +order_id: string
      +transaction_type: string
      +points: int
    }

    User "1" --> "0..1" Runner : profile
    User "1" --> "0..1" Cart : owns
    Cart "1" --> "0..*" CartItem : contains
    CartItem "*" --> "1" Food : references

    User "1" --> "0..*" Checkout : starts
    Checkout "0..1" --> "1" Order : confirms

    User "1" --> "0..*" Order : places
    Order "1" --> "1..*" OrderItem : has
    OrderItem "*" --> "1" Food : points_to

    Order "1" --> "0..1" Delivery : fulfillment
    Delivery "*" --> "0..1" User : runner
    Order "1" --> "0..*" OrderOTP : verification

    Order "1" --> "0..*" Payment : paid_by
    User "1" --> "0..*" Payment : initiates

    User "1" --> "0..*" Review : writes
    Review "*" --> "1" Food : rates
    Review "*" --> "0..1" Order : from_order

    User "1" --> "0..*" Notification : receives

    User "1" --> "0..1" RewardPoints : wallet
    RewardPoints "1" --> "0..*" RewardTransaction : ledger
    RewardTransaction "*" --> "0..1" Order : linked_order
```

## 2) Sequence Diagram: Checkout to Order Creation

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant FE as Frontend App
    participant API as Flask API (/api/checkout)
    participant DB as SQLite/SQLAlchemy
    participant Mail as Email Service

    Customer->>FE: Submit checkout form + items
    FE->>API: POST /api/checkout
    API->>API: Validate address, phone, payment method, items

    alt Validation fails
      API-->>FE: 400 validation_errors
      FE-->>Customer: Show field errors
    else Validation succeeds
      loop For each item
        API->>DB: Fetch Food price by food_id
      end
      API->>API: Compute subtotal/tax/delivery/discount/final_total
      API->>DB: Insert Order + OrderItems
      API->>DB: Insert Delivery (pending)
      API->>DB: Insert Checkout (confirmed)
      API->>DB: Insert Pickup OTP + Delivery OTP
      API->>DB: Commit transaction
      API->>Mail: Send order confirmation + admin notification
      API-->>FE: 201 order_id + order_number + OTPs
      FE-->>Customer: Show confirmation screen
    end
```

## 3) Sequence Diagram: Payment Initiation and Confirmation

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant FE as Frontend App
    participant PayAPI as Flask API (/api/payment)
    participant DB as SQLite/SQLAlchemy
    participant PSP as Razorpay (or Mock)

    Customer->>FE: Choose payment method (cod/upi/card)
    FE->>PayAPI: POST /api/payment/initiate
    PayAPI->>DB: Validate user + order ownership + order state
    PayAPI->>DB: Check payment attempt rate limit

    alt COD
      PayAPI->>DB: Create Payment(status=pending)
      PayAPI->>DB: Update Order(status=confirmed, payment_status=cod_pending)
      PayAPI-->>FE: COD accepted
    else UPI
      PayAPI->>PSP: Create order (or mock)
      PayAPI->>DB: Create Payment(status=pending, razorpay_order_id)
      PayAPI-->>FE: return key_id + order_id
      FE->>PSP: Complete checkout
      FE->>PayAPI: POST /api/payment/verify
      PayAPI->>PSP: Verify signature
      PayAPI->>DB: Mark Payment success; Order paid/confirmed
      PayAPI-->>FE: Payment verified
    else CARD
      PayAPI->>PayAPI: Validate Luhn + expiry + PIN format
      PayAPI->>DB: Create Payment(status=success)
      PayAPI->>DB: Update Order(status=confirmed, payment_status=paid)
      PayAPI-->>FE: Card payment success
    end
```

## 4) High-Level Service Interaction Diagram

```mermaid
flowchart LR
    U[Customer / Runner / Staff]
    FE[React Frontend]
    API[Flask API Blueprints]
    DB[(SQLite via SQLAlchemy)]
    WS[Socket.IO]
    MAIL[SMTP / Gmail]
    PSP[Razorpay]

    U --> FE
    FE --> API
    API --> DB
    API --> WS
    API --> MAIL
    API --> PSP

    subgraph API Modules
      AUTH[auth_routes]
      CART[cart_routes]
      CHECKOUT[checkout_routes]
      ORDER[order_routes]
      RUNNER[runner_routes]
      PAY[payment_routes]
      REVIEW[review_routes]
      NOTIF[notification_routes]
      REWARD[rewards_routes]
    end

    FE --> AUTH
    FE --> CART
    FE --> CHECKOUT
    FE --> ORDER
    FE --> RUNNER
    FE --> PAY
    FE --> REVIEW
    FE --> NOTIF
    FE --> REWARD
```

## Notes

- Diagrams are based on the current backend model and route flow.
- Update this file whenever model relationships or key endpoints change.
