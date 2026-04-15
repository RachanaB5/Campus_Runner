# CampusRunner

> A real-time campus canteen ordering and delivery platform built for RV University.  
> Students browse the menu, place orders, and track them live. A unique **Runner Mode** lets any student volunteer as a delivery agent and earn reward points.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Docker](#docker)
- [Agile Development](#agile-development)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | Description |
|---|---|
| **Menu & Ordering** | Browse categorized food items, add to cart, place orders |
| **Runner Mode** | Toggle into runner mode to accept and deliver orders, earn reward points |
| **Real-Time Tracking** | Live order status updates pushed via Socket.IO |
| **Digital Tokens** | Unique token per order for counter identification |
| **FCFS Queue** | Fair first-come-first-served order processing with row-locking to prevent race conditions |
| **Payment Integration** | Razorpay (UPI/card) + Cash on Delivery, with saved payment methods |
| **OTP Verification** | Pickup OTP + delivery OTP per order for secure handoff |
| **Order Cancellation** | Cancel pending/prep orders, auto-release assigned runner, mark online payments as refunded |
| **Reward Points** | Points earned per delivery, tiered system with transaction ledger |
| **Admin Dashboard** | Manage menu items, view/update orders, manage users, analytics |
| **Email Notifications** | Order confirmations, OTP emails, admin alerts via Gmail SMTP |
| **In-App Notifications** | Real-time bell notifications stored in DB and pushed via Socket.IO |
| **Food Reviews** | Star ratings and comments per order item |
| **Image Uploads** | Menu item images via Cloudinary |

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend | React | 18.3.1 |
| Language | TypeScript | 5.x |
| Build Tool | Vite | 6.3.5 |
| Styling | Tailwind CSS | 4.x |
| UI Components | Radix UI + shadcn/ui | — |
| Charts | Recharts | 2.x |
| Backend | Python / Flask | 2.3.3 |
| Realtime | Flask-SocketIO / Socket.IO | 5.x / 4.x |
| Database | SQLite via SQLAlchemy | 2.0 |
| Auth | Flask-JWT-Extended | 4.5.3 |
| Payments | Razorpay | — |
| Email | Flask-Mail (Gmail SMTP) | 0.9.1 |
| Image CDN | Cloudinary | — |
| Rate Limiting | Flask-Limiter | 3.5.0 |
| PDF Generation | ReportLab | 4.x |
| Testing (BE) | Pytest + pytest-cov | 8.x |
| Testing (FE) | Vitest + Testing Library | 2.x |
| CI/CD | GitHub Actions | — |
| Containerization | Docker + Docker Compose | — |
| Web Server | Gunicorn + Eventlet | — |
| Reverse Proxy | Nginx | — |

---

## Project Structure

```
Campus_Runner/
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── food.py
│   │   ├── cart.py
│   │   ├── checkout.py
│   │   ├── order.py
│   │   ├── delivery.py
│   │   ├── runner.py
│   │   ├── payment.py
│   │   ├── saved_payment_method.py
│   │   ├── otp.py
│   │   ├── token.py
│   │   ├── notification.py
│   │   ├── review.py
│   │   └── reward_points.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── menu_routes.py
│   │   ├── cart_routes.py
│   │   ├── checkout_routes.py
│   │   ├── order_routes.py
│   │   ├── runner_routes.py
│   │   ├── payment_routes.py
│   │   ├── payment_methods_routes.py
│   │   ├── rewards_routes.py
│   │   ├── notification_routes.py
│   │   ├── review_routes.py
│   │   └── staff_admin_routes.py
│   ├── services/
│   │   ├── notification_service.py
│   │   └── payment_service.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_admin.py
│   │   ├── test_cart_checkout_orders.py
│   │   ├── test_menu_and_reviews.py
│   │   ├── test_orders_and_notifications.py
│   │   ├── test_payment_methods.py
│   │   ├── test_rewards.py
│   │   └── test_runner_and_delivery.py
│   ├── app.py                  # Entry point — DB init, blueprints, Socket.IO
│   ├── seed.py                 # Seed sample reviews & sync menu catalog
│   ├── socketio_events.py      # Socket.IO event handlers
│   ├── utils.py                # Shared utilities (email, OTP, etc.)
│   └── requirements.txt
├── src/
│   ├── app/
│   │   ├── components/         # Reusable UI components
│   │   │   └── ui/             # shadcn/ui primitives
│   │   ├── context/            # AuthContext, CartContext
│   │   ├── data/               # Static/mock data
│   │   ├── hooks/              # useSocket, useNotifications, useOrderTracking, useRunnerState
│   │   ├── pages/              # Route-level pages
│   │   ├── services/           # api.ts, socket.ts
│   │   └── utils/              # foodImages, helpers
│   ├── styles/                 # Global CSS, Tailwind, theme
│   ├── test/setup.ts
│   └── main.tsx
├── .env.example                # All environment variable templates
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Main CI/CD pipeline
│   │   ├── codeql.yml          # CodeQL security analysis
│   │   └── security.yml        # Trivy security scan
│   ├── CODEOWNERS
│   └── dependabot.yml
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-entrypoint.sh
├── nginx.conf
├── nginx-default.conf
├── Makefile
├── package.json
├── pytest.ini
├── DEVOPS.md
└── README.md
```

---

## Getting Started

### Prerequisites

- Python **3.11+**
- Node.js **20+** and npm
- Git

### 1. Clone

```bash
git clone https://github.com/RachanaB5/campusrunner.git
cd campusrunner
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values. At minimum set `JWT_SECRET_KEY` and `SECRET_KEY`. See [Environment Variables](#environment-variables) for the full list.

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

- API runs at `http://localhost:5000`
- Database (`instance/campusrunner.db`) and the default admin account are created automatically on first run
- Menu catalog is seeded automatically if the database is empty

> **Default admin credentials:** `admin@rvu.edu.in` / `admin@123`

### 4. Start the frontend

```bash
# from project root
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values.

### Core

| Variable | Default | Description |
|---|---|---|
| `FLASK_ENV` | `development` | Flask environment |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |
| `SECRET_KEY` | — | Flask session secret key |
| `JWT_SECRET_KEY` | — | Secret for signing JWT tokens |
| `DATABASE_URL` | `sqlite:///campusrunner.db` | Database connection string |

### URLs & CORS

| Variable | Default | Description |
|---|---|---|
| `FRONTEND_URL` | `http://localhost:5173` | Frontend origin for CORS |
| `VITE_API_URL` | `http://localhost:5000` | Backend URL used by the frontend |
| `CORS_ORIGINS` | *(localhost variants)* | Comma-separated allowed origins |
| `ALLOWED_EMAIL_DOMAIN` | `rvu.edu.in` | Restrict signups to this domain |

### Email (Gmail SMTP)

| Variable | Description |
|---|---|
| `MAIL_SERVER` | SMTP server (default: `smtp.gmail.com`) |
| `MAIL_PORT` | SMTP port (default: `587`) |
| `MAIL_USE_TLS` | Enable TLS (default: `True`) |
| `MAIL_USERNAME` | Gmail address |
| `MAIL_PASSWORD` | Gmail app password (16 chars, no spaces) |
| `MAIL_DEFAULT_SENDER` | From address for outgoing emails |

### Payments

| Variable | Description |
|---|---|
| `RAZORPAY_KEY_ID` | Razorpay API key ID |
| `RAZORPAY_KEY_SECRET` | Razorpay API secret |

### Image Uploads

| Variable | Description |
|---|---|
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

---

## API Reference

All endpoints are prefixed with `/api`.

### Auth — `/api/auth`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/register` | Register a new user |
| `POST` | `/login` | Login, returns JWT |
| `POST` | `/verify-email` | Verify email with OTP |
| `POST` | `/forgot-password` | Request password reset |
| `POST` | `/reset-password` | Reset password with token |
| `GET` | `/me` | Get current user profile |

### Menu — `/api/menu`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List all available food items |
| `GET` | `/<id>` | Get a single food item |
| `POST` | `/` | Create food item *(admin)* |
| `PUT` | `/<id>` | Update food item *(admin)* |
| `DELETE` | `/<id>` | Delete food item *(admin)* |

### Cart — `/api/cart`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Get current user's cart |
| `POST` | `/add` | Add item to cart |
| `PUT` | `/update` | Update item quantity |
| `DELETE` | `/remove/<item_id>` | Remove item from cart |
| `DELETE` | `/clear` | Clear entire cart |

### Checkout — `/api/checkout`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/` | Create order from cart |

### Orders — `/api/order`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List user's orders |
| `GET` | `/<id>` | Get order details |
| `POST` | `/<id>/cancel` | Cancel an order |
| `GET` | `/public` | Public order board (all active orders) |

### Payments — `/api/payment`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/initiate` | Initiate payment (COD / UPI / card) |
| `POST` | `/verify` | Verify Razorpay payment signature |

### Payment Methods — `/api/payment-methods`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List saved payment methods |
| `POST` | `/` | Save a payment method |
| `DELETE` | `/<id>` | Delete a saved method |

### Runner — `/api/runner`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/toggle` | Toggle runner mode on/off |
| `GET` | `/available-orders` | List orders available to claim |
| `POST` | `/claim/<order_id>` | Claim an order (FCFS with row-lock) |
| `POST` | `/update-status` | Update delivery status |
| `POST` | `/confirm-otp` | Confirm delivery with OTP |
| `GET` | `/my-deliveries` | Runner's delivery history |

### Rewards — `/api/rewards`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Get reward points balance and tier |
| `GET` | `/transactions` | Get points transaction history |

### Notifications — `/api/notifications`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List user's notifications |
| `POST` | `/<id>/read` | Mark notification as read |
| `POST` | `/read-all` | Mark all as read |

### Reviews — `/api/reviews`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/` | Submit a review for an order item |
| `GET` | `/food/<food_id>` | Get reviews for a food item |

### Admin — `/api/admin`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users` | List all users |
| `GET` | `/orders` | List all orders |
| `PUT` | `/orders/<id>/status` | Update order status |
| `GET` | `/analytics` | Dashboard analytics |
| `POST` | `/menu` | Add menu item |
| `PUT` | `/menu/<id>` | Edit menu item |
| `DELETE` | `/menu/<id>` | Delete menu item |

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |

---

## Running Tests

### Backend

```bash
cd backend
pytest
```

With coverage:

```bash
pytest --cov=backend --cov-report=term-missing --cov-report=xml
```

Test files:

| File | Coverage |
|---|---|
| `test_auth.py` | Registration, login, email verification, password reset |
| `test_admin.py` | Admin user/order/menu management |
| `test_cart_checkout_orders.py` | Cart operations, checkout flow, order creation |
| `test_menu_and_reviews.py` | Menu CRUD, food reviews |
| `test_orders_and_notifications.py` | Order lifecycle, cancellation, notifications |
| `test_payment_methods.py` | Saved payment methods |
| `test_rewards.py` | Reward points, tiers, transactions |
| `test_runner_and_delivery.py` | Runner mode, order claiming, delivery OTP |

### Frontend

```bash
npm test
```

With coverage:

```bash
npm run test:coverage
```

Other scripts:

```bash
npm run lint        # ESLint
npm run typecheck   # TypeScript type check
npm run build       # Production build
```

---

## CI/CD Pipeline

`.github/workflows/ci.yml` runs on every push and pull request.

### Jobs

| Job | Trigger | What it does |
|---|---|---|
| `backend` | PR or `backend/` changes | flake8 lint + pytest (Python 3.11 & 3.12) + Codecov upload |
| `frontend-setup` | PR or `src/` changes | `npm ci` + cache `node_modules` |
| `frontend-lint` | after setup | `npm run lint` |
| `frontend-typecheck` | after setup | `npm run typecheck` |
| `frontend-test` | after lint + typecheck | Vitest with coverage + Codecov upload |
| `frontend-build` | after tests | `npm run build` + artifact upload (14 days) |
| `docker-build` | push to `main`/`develop`/`feature/*`/`fix/*` | Build & push backend + frontend images to GHCR |
| `security` | always | Trivy filesystem scan → SARIF upload |
| `deployment-ready` | push to `main` (all jobs pass) | Deployment summary |

### Additional workflows

| File | Description |
|---|---|
| `codeql.yml` | Weekly CodeQL static analysis (Python + JavaScript) |
| `security.yml` | Trivy vulnerability scan |
| `dependabot.yml` | Weekly dependency updates for npm, pip, Docker, Actions |

See [DEVOPS.md](./DEVOPS.md) for the full Docker & DevOps reference.

---

## Docker

### Development

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Production

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### Default (single command)

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | `http://localhost:5173` |
| Backend API | `http://localhost:5000` |

Images are published to GitHub Container Registry (`ghcr.io`) on every push to `main`, `develop`, `feature/*`, and `fix/*` branches.

---

## Agile Development

Built using Agile methodology with sprint-based delivery at RV University.

**Sprint 1** — User auth, email verification, menu display, cart, basic order placement

**Sprint 2** — Payment integration (Razorpay + COD), digital tokens, FCFS queue, runner mode, OTP delivery confirmation, reward points, public order board

**Definition of Done:** Code implemented → persisted in DB → UI working → no critical bugs → tested → integrated → reviewed

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to your fork: `git push origin feature/your-feature`
5. Open a Pull Request against `main`

Branch naming: `feature/`, `fix/`, `chore/`, `docs/`

---

## License

MIT
