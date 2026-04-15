#!/bin/bash
# Campus Runner — Start All Services
# Usage: ./start.sh
# Kills any stale processes on ports 5000 & 5173, then starts backend + frontend.

set -e
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀  Campus Runner — Starting All Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Kill anything on ports 5000 and 5173
echo ""
echo "🔄  Freeing ports 5000 and 5173..."
lsof -ti:5000 | xargs kill -9 2>/dev/null && echo "  Killed process on port 5000" || echo "  Port 5000 already free"
lsof -ti:5173 | xargs kill -9 2>/dev/null && echo "  Killed process on port 5173" || echo "  Port 5173 already free"
sleep 1

# 2. Activate Python venv
VENV="$PROJECT_ROOT/.venv"
if [ -d "$VENV" ]; then
  source "$VENV/bin/activate"
  echo "✅  Python venv activated"
else
  echo "⚠️  No .venv found at $VENV — make sure you've run: python3 -m venv .venv && pip install -r backend/requirements.txt"
fi

# 3. Start Flask backend
echo ""
echo "🐍  Starting Flask backend on http://localhost:5000 ..."
cd "$PROJECT_ROOT/backend"
python app.py &
BACKEND_PID=$!
echo "     Backend PID: $BACKEND_PID"
cd "$PROJECT_ROOT"

# Wait for backend to be ready
sleep 3
if ! lsof -ti:5000 > /dev/null 2>&1; then
  echo "❌  Backend failed to start. Check logs above."
  exit 1
fi
echo "✅  Backend is up!"

# 4. Start Vite frontend
echo ""
echo "⚡  Starting Vite frontend on http://localhost:5173 ..."
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
npm --prefix "$PROJECT_ROOT" run dev &
FRONTEND_PID=$!
echo "     Frontend PID: $FRONTEND_PID"
sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  All services are running!"
echo ""
echo "  🌐  Frontend :  http://localhost:5173"
echo "  🔧  Backend  :  http://localhost:5000"
echo "  📡  Health   :  http://localhost:5000/api/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Press Ctrl+C to stop all services."
echo ""

# Trap Ctrl+C to kill both
cleanup() {
  echo ""
  echo "🛑  Stopping all services..."
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  lsof -ti:5000 | xargs kill -9 2>/dev/null || true
  lsof -ti:5173 | xargs kill -9 2>/dev/null || true
  echo "✅  All services stopped."
  exit 0
}

trap cleanup INT TERM

wait
