def test_customer_can_cancel_pending_order(client, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    food = make_food()
    order, _delivery = make_order(
        customer=customer,
        items=[(food, 1, None)],
        status="confirmed",
        delivery_status="pending",
    )

    response = client.post(f"/api/order/{order.id}/cancel", headers=auth_headers(customer))
    assert response.status_code == 200

    from models import Order
    updated = Order.query.get(order.id)
    assert updated.status == "cancelled"


def test_customer_cannot_cancel_in_transit_order(client, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    food = make_food()
    order, _delivery = make_order(
        customer=customer,
        items=[(food, 1, None)],
        status="out_for_delivery",
        delivery_status="on_the_way",
    )

    response = client.post(f"/api/order/{order.id}/cancel", headers=auth_headers(customer))
    assert response.status_code == 400


def test_other_user_cannot_cancel_order(client, make_user, make_food, make_order, auth_headers):
    owner = make_user(email="owner@rvu.edu.in")
    other = make_user(email="other@rvu.edu.in")
    food = make_food()
    order, _delivery = make_order(customer=owner, items=[(food, 1, None)], status="confirmed")

    response = client.post(f"/api/order/{order.id}/cancel", headers=auth_headers(other))
    assert response.status_code in (403, 404)


def test_cancel_paid_order_marks_refund_and_releases_runner(client, make_user, make_food, make_order, make_runner, auth_headers):
    import uuid
    from models import Order, Payment, Delivery, Runner, db

    customer = make_user(email="paid-cancel@rvu.edu.in")
    runner_user, _runner = make_runner(email="runner-cancel@rvu.edu.in", status="on_delivery")
    food = make_food(name="Refund Bowl", price=120)
    order, delivery = make_order(
        customer=customer,
        items=[(food, 1, None)],
        status="confirmed",
        payment_status="paid",
        delivery_status="assigned",
        runner_user_id=runner_user.id,
    )

    payment = Payment(
        id=str(uuid.uuid4()),
        order_id=order.id,
        user_id=customer.id,
        method="card",
        razorpay_order_id=f"order_test_{uuid.uuid4().hex[:8]}",
        razorpay_payment_id=f"pay_test_{uuid.uuid4().hex[:8]}",
        amount=int(round(float(order.total_amount) * 100)),
        currency="INR",
        status="success",
    )
    db.session.add(payment)
    db.session.commit()

    response = client.post(f"/api/order/{order.id}/cancel", headers=auth_headers(customer))
    assert response.status_code == 200

    updated_order = Order.query.get(order.id)
    updated_payment = Payment.query.get(payment.id)
    updated_delivery = Delivery.query.get(delivery.id)
    runner_profile = Runner.query.filter_by(user_id=runner_user.id).first()

    assert updated_order.status == "cancelled"
    assert updated_order.payment_status == "refunded"
    assert updated_payment.status == "refunded"
    assert updated_delivery.status == "cancelled"
    assert updated_delivery.runner_id is None
    assert runner_profile.status == "online"


def test_order_detail_returns_items_and_status(client, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    food = make_food(name="Chicken Roll", price=100)
    order, _delivery = make_order(customer=customer, items=[(food, 3, "Extra spicy")])

    response = client.get(f"/api/order/{order.id}", headers=auth_headers(customer))
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == order.id
    assert len(data["items"]) == 1
    assert data["items"][0]["food_name"] == "Chicken Roll"
    assert data["items"][0]["quantity"] == 3


def test_notifications_created_on_checkout(client, make_user, make_food, auth_headers):
    from models import Notification

    user = make_user(email="notify@rvu.edu.in")
    food = make_food(name="Paneer Burger", price=90)

    client.post("/api/checkout", json={
        "items": [{"food_id": food.id, "quantity": 1, "price": 90}],
        "delivery_address": "Hostel C, Room 301",
        "delivery_city": "Bangalore",
        "delivery_pincode": "560001",
        "customer_phone": "9876543210",
        "payment_method": "cod",
        "subtotal": 90,
        "tax_amount": 4.5,
        "delivery_fee": 10,
        "final_total": 104.5,
    }, headers=auth_headers(user))

    notifications = Notification.query.filter_by(user_id=user.id).all()
    assert len(notifications) >= 1


def test_notifications_list_and_mark_read(client, make_user, make_food, auth_headers):
    from models import Notification, db
    import uuid

    user = make_user(email="notif@rvu.edu.in")
    db.session.add(Notification(
        id=str(uuid.uuid4()),
        user_id=user.id,
        title="Test Notification",
        message="Your order is ready",
        type="order_update",
        is_read=False,
    ))
    db.session.commit()

    list_response = client.get("/api/notifications", headers=auth_headers(user))
    assert list_response.status_code == 200
    notifications = list_response.get_json()["notifications"]
    assert len(notifications) >= 1
    assert notifications[0]["is_read"] is False

    mark_response = client.put("/api/notifications/read-all", headers=auth_headers(user))
    assert mark_response.status_code == 200

    after = client.get("/api/notifications?unread=true", headers=auth_headers(user))
    assert len(after.get_json()["notifications"]) == 0
