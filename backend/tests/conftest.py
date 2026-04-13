import importlib
import os
import sys
import uuid
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _clear_backend_modules():
    prefixes = ("models", "routes.", "services.")
    exact = {"app", "seed", "socketio_events", "utils"}
    for module_name in list(sys.modules):
        if module_name in exact or module_name.startswith(prefixes):
            sys.modules.pop(module_name, None)


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("pytest-db")
    db_path = db_dir / "campusrunner-test.sqlite"

    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["JWT_SECRET_KEY"] = "pytest-secret-key"
    os.environ["MAIL_SERVER"] = ""
    os.environ["MAIL_USERNAME"] = ""
    os.environ["MAIL_PASSWORD"] = ""
    os.environ["MAIL_DEFAULT_SENDER"] = "pytest@campusrunner.local"

    _clear_backend_modules()
    app_module = importlib.import_module("app")
    flask_app = app_module.app
    flask_app.config.update(
        TESTING=True,
        MAIL_SUPPRESS_SEND=True,
    )

    import routes.auth_routes as auth_routes
    import routes.checkout_routes as checkout_routes
    import utils

    auth_routes.dispatch_otp_email = lambda *args, **kwargs: (False, None)
    checkout_routes.send_order_confirmation_email = lambda *args, **kwargs: True
    utils.send_admin_order_notification = lambda *args, **kwargs: True
    utils.send_email_in_background = lambda *args, **kwargs: None

    if getattr(app_module, "socketio", None):
        app_module.socketio.emit = lambda *args, **kwargs: None

    with flask_app.app_context():
        app_module.db.drop_all()
        app_module.db.create_all()

    yield flask_app


@pytest.fixture(autouse=True)
def reset_database(app):
    from models import db
    import routes.auth_routes as auth_routes

    with app.app_context():
        db.drop_all()
        db.create_all()
        auth_routes.otp_store.clear()
        yield
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(app):
    from models import RewardPoints, User, db

    counter = {"value": 0}

    def _make_user(
        *,
        name="Test User",
        email=None,
        password="password123",
        phone="9876543210",
        role="customer",
        is_verified=True,
        with_rewards=True,
    ):
        counter["value"] += 1
        user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email or f"user{counter['value']}@rvu.edu.in",
            phone=phone,
            role=role,
            is_verified=is_verified,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if with_rewards:
            reward = RewardPoints(
                id=str(uuid.uuid4()),
                user_id=user.id,
                total_points=0,
                points_balance=0,
                tier="bronze",
            )
            db.session.add(reward)

        db.session.commit()
        return user

    return _make_user


@pytest.fixture
def make_food(app):
    from models import Food, db

    counter = {"value": 0}

    def _make_food(
        *,
        name=None,
        category="Burgers",
        price=120.0,
        description="Tasty campus food",
        is_veg=True,
        prep_time=15,
        available=True,
    ):
        counter["value"] += 1
        food = Food(
            id=str(uuid.uuid4()),
            name=name or f"Food {counter['value']}",
            description=description,
            price=price,
            category=category,
            prep_time=prep_time,
            available=available,
            is_veg=is_veg,
            rating=4.5,
            review_count=0,
        )
        db.session.add(food)
        db.session.commit()
        return food

    return _make_food


@pytest.fixture
def make_runner(app, make_user):
    from models import Runner, db

    counter = {"value": 0}

    def _make_runner(*, user=None, name="Runner User", email=None, is_available=True, status="online"):
        counter["value"] += 1
        runner_user = user or make_user(
            name=name,
            email=email or f"runner{counter['value']}@rvu.edu.in",
            role="runner",
        )
        runner = Runner(
            id=str(uuid.uuid4()),
            user_id=runner_user.id,
            vehicle_type="bike",
            license_number=f"LIC-{counter['value']}",
            is_available=is_available,
            status=status,
            total_deliveries=0,
            average_rating=4.8,
        )
        db.session.add(runner)
        db.session.commit()
        return runner_user, runner

    return _make_runner


@pytest.fixture
def auth_headers(app):
    from flask_jwt_extended import create_access_token

    def _auth_headers(user):
        with app.app_context():
            token = create_access_token(identity=user.id)
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


@pytest.fixture
def make_order(app):
    from models import Delivery, Food, Order, OrderItem, OrderOTP, RewardPoints, db

    def _make_order(
        *,
        customer,
        items,
        status="confirmed",
        payment_method="upi",
        payment_status="paid",
        delivery_status="pending",
        delivery_address="Hostel A, Room 101, Near Block A",
        customer_phone="9876543210",
        special_instructions="",
        create_otps=False,
        runner_user_id=None,
    ):
        subtotal = 0.0
        order = Order(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            order_number=f"ORD-TEST-{str(uuid.uuid4())[:6].upper()}",
            status=status,
            total_amount=0.0,
            delivery_fee=10.0,
            payment_status=payment_status,
            payment_method=payment_method,
            delivery_address=delivery_address,
            customer_phone=customer_phone,
            special_instructions=special_instructions,
        )
        db.session.add(order)
        db.session.flush()

        for food, quantity, customizations in items:
            if isinstance(food, str):
                food = Food.query.get(food)
            total_price = float(food.price) * quantity
            subtotal += total_price
            db.session.add(OrderItem(
                id=str(uuid.uuid4()),
                order_id=order.id,
                food_id=food.id,
                quantity=quantity,
                unit_price=food.price,
                total_price=total_price,
                customizations=customizations,
            ))

        order.total_amount = subtotal + order.delivery_fee
        delivery = Delivery(
            id=str(uuid.uuid4()),
            order_id=order.id,
            runner_id=runner_user_id,
            status=delivery_status,
            delivery_location=delivery_address,
            estimated_time_minutes=30,
        )
        db.session.add(delivery)

        if create_otps:
            db.session.add(OrderOTP.create_for_order(order.id, delivery.id, otp_type="pickup"))
            db.session.add(OrderOTP.create_for_order(order.id, delivery.id, otp_type="delivery"))

        reward = RewardPoints.query.filter_by(user_id=customer.id).first()
        if not reward:
            db.session.add(RewardPoints(
                id=str(uuid.uuid4()),
                user_id=customer.id,
                total_points=0,
                points_balance=0,
                tier="bronze",
            ))

        db.session.commit()
        return Order.query.get(order.id), Delivery.query.get(delivery.id)

    return _make_order
