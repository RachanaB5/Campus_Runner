# CampusRunner

A real-time campus canteen ordering and delivery platform. Students can browse the menu, place orders, and track them live. A unique **Runner Mode** lets users volunteer as delivery agents and earn reward points.

---

## Features

- **Menu & Ordering** — Browse categorized food items, add to cart, and place orders
- **Runner Mode** — Users toggle into runner mode to accept and deliver orders, earning reward points
- **Real-Time Tracking** — Live order status updates via Socket.IO
- **Token System** — Digital tokens for order identification at the counter
- **FCFS Queue** — Fair first-come-first-served order processing
- **Payment Integration** — Razorpay with saved payment methods
- **OTP Verification** — Delivery confirmation via OTP
- **Admin Dashboard** — Manage menu, orders, users, and view analytics
- **Email Notifications** — Order confirmations and OTP emails via Gmail/SMTP
- **Order Cancellation + Refund Handling** — Cancels pending/prep orders, releases assigned runners, and marks successful online payments as refunded
- **FCFS Runner Claim Guard** — Runner order acceptance uses row-locking logic to reduce race conditions in first-come-first-served flow

---

## Tech Stack

| Layer     | Technology                              |
|-----------|-----------------------------------------|
| Frontend  | React 18, TypeScript, Vite, Tailwind CSS |
| Backend   | Python, Flask, Flask-SocketIO           |
| Database  | SQLite (via SQLAlchemy)                 |
| Auth      | JWT (Flask-JWT-Extended)                |
| Payments  | Razorpay                                |
| Realtime  | Socket.IO                               |
| Testing   | Pytest (backend), Vitest (frontend)     |
| CI        | GitHub Actions                          |

---

## Project Structure

```
Campus_Runner/
├── backend/                  # Flask API
│   ├── models/               # SQLAlchemy models
│   ├── routes/               # API blueprints
│   ├── services/             # Business logic (payments, notifications)
│   ├── tests/                # Pytest test suite
│   ├── app.py                # App entry point & DB init
│   ├── seed.py               # Seed sample data
│   ├── utils.py              # Shared utilities
│   ├── socketio_events.py    # Socket.IO event handlers
│   └── requirements.txt
├── src/                      # React frontend
│   ├── app/
│   │   ├── components/       # Reusable UI components
│   │   ├── context/          # Auth & Cart context
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Route-level page components
│   │   └── services/         # API & Socket clients
│   └── main.tsx
├── .env.example              # Environment variable template
├── .github/workflows/ci.yml  # CI pipeline
├── package.json              # Frontend dependencies
└── pytest.ini                # Pytest config
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm

### 1. Clone the repo

```bash
git clone https://github.com/your-username/campusrunner.git
cd campusrunner
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your values (JWT secret, Razorpay keys, email credentials). See `.env.example` for all available options.

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Shortcut command:

```bash
cd backend && pip install -r requirements.txt && python app.py
```

The API runs at `http://localhost:5000`. The database and a default admin account are created automatically on first run.

> Default admin: `admin@rvu.edu.in` / `admin@123`

### 4. Start the frontend

```bash
# from project root
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

### 5. Run with Docker Compose (optional)

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000`

---

## Running Tests

**Backend**
```bash
cd backend
pytest
```

**Frontend**
```bash
npm test
```

Coverage commands:

```bash
# backend coverage
cd backend
pytest --cov=backend --cov-report=term-missing --cov-report=xml

# frontend coverage
cd ..
npm run test:coverage
```

## CI Workflows

- `.github/workflows/ci.yml`: backend tests (Py 3.11/3.12), frontend lint, typecheck, tests, and build (`npm run build`), with coverage/build artifacts uploaded.
- `.github/workflows/test.yml`: focused backend/frontend test workflow with coverage artifacts.

See [DEVOPS.md](./DEVOPS.md) for the full Docker & DevOps reference.

This repository already ignores `dist/` in `.gitignore`; CI builds frontend artifacts in workflow runs instead of relying on committed build output.

## Notification Channels

- Implemented: in-app notifications (DB + Socket.IO real-time events) and email.
- Not yet implemented: browser/mobile push notification delivery (Web Push / FCM / APNs).

---

## API Overview

| Prefix                  | Description              |
|-------------------------|--------------------------|
| `POST /api/auth/*`      | Register, login, OTP     |
| `GET  /api/menu/*`      | Browse food items        |
| `POST /api/cart/*`      | Manage cart              |
| `POST /api/order/*`     | Place & track orders     |
| `POST /api/checkout/*`  | Checkout flow            |
| `POST /api/payment/*`   | Razorpay payment         |
| `GET  /api/runner/*`    | Runner mode endpoints    |
| `GET  /api/rewards/*`   | Reward points            |
| `GET  /api/admin/*`     | Admin management         |
| `GET  /api/health`      | Health check             |

---

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable              | Description                        |
|-----------------------|------------------------------------|
| `JWT_SECRET_KEY`      | Secret for signing JWT tokens      |
| `DATABASE_URL`        | SQLite path (default: auto-set)    |
| `RAZORPAY_KEY_ID`     | Razorpay API key                   |
| `RAZORPAY_KEY_SECRET` | Razorpay secret                    |
| `MAIL_USERNAME`       | Gmail address for sending emails   |
| `MAIL_PASSWORD`       | Gmail app password (16 chars)      |
| `ALLOWED_EMAIL_DOMAIN`| Restrict signups to a domain       |

---

## Agile Development

This project was built using Agile methodology with sprint-based delivery.

**Sprint 1** — User auth, menu display, cart, basic order placement  
**Sprint 2** — Payment integration, digital tokens, FCFS queue, public order display

**Definition of Done:** Code implemented → stored in DB → UI working → no critical bugs → tested → integrated

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push and open a Pull Request

---

## License

MIT
