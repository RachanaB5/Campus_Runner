def test_runner_available_orders_returns_display_ready_payload(client, make_user, make_runner, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    runner_user, _runner = make_runner(email="runner@rvu.edu.in")
    food = make_food(name="Paneer Roll", price=85)
    order, _delivery = make_order(
        customer=customer,
        items=[(food, 2, "Spice level: Spicy")],
        status="confirmed",
        delivery_status="pending",
    )

    response = client.get("/api/runner/available-orders", headers=auth_headers(runner_user))
    assert response.status_code == 200
    payload = response.get_json()["orders"][0]
    assert payload["order_id"] == order.id
    assert payload["token_number"] == order.order_number
    assert payload["customer_name"].startswith("Test")
    assert payload["items"][0]["name"] == "Paneer Roll"
    assert payload["total_amount"] == order.total_amount
    assert payload["payment_status"] == "paid"


def test_runner_accept_order_and_fetch_active_delivery(client, make_user, make_runner, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    runner_user, _runner = make_runner(email="runner@rvu.edu.in")
    food = make_food(name="Cold Coffee", category="Beverages", price=55)
    order, delivery = make_order(
        customer=customer,
        items=[(food, 1, None)],
        status="confirmed",
        delivery_status="pending",
        create_otps=True,
    )

    accept_response = client.post(f"/api/runner/accept/{order.id}", headers=auth_headers(runner_user))
    assert accept_response.status_code == 200
    accept_payload = accept_response.get_json()
    assert accept_payload["delivery_id"] == delivery.id
    assert accept_payload["pickup_otp"]

    active_response = client.get("/api/runner/active-delivery", headers=auth_headers(runner_user))
    assert active_response.status_code == 200
    active_payload = active_response.get_json()
    assert active_payload["active"] is True
    assert active_payload["delivery_id"] == delivery.id
    assert active_payload["details"]["order_id"] == order.id


def test_runner_delivery_status_requires_correct_otp_and_awards_points(client, make_user, make_runner, make_food, make_order, auth_headers):
    from models import OrderOTP, RewardPoints

    customer = make_user(email="customer@rvu.edu.in")
    runner_user, _runner = make_runner(email="runner@rvu.edu.in")
    food = make_food(name="Masala Fries", price=60)
    order, delivery = make_order(
        customer=customer,
        items=[(food, 2, None)],
        status="confirmed",
        delivery_status="assigned",
        create_otps=True,
        runner_user_id=runner_user.id,
    )

    pickup_response = client.put(
        f"/api/runner/delivery/{delivery.id}/status",
        json={"status": "picked_up"},
        headers=auth_headers(runner_user),
    )
    assert pickup_response.status_code == 200

    wrong_otp_response = client.put(
        f"/api/runner/delivery/{delivery.id}/status",
        json={"status": "delivered", "otp": "0000"},
        headers=auth_headers(runner_user),
    )
    assert wrong_otp_response.status_code == 400

    delivery_otp = OrderOTP.query.filter_by(order_id=order.id, delivery_id=delivery.id, otp_type="delivery").first()
    correct_response = client.put(
        f"/api/runner/delivery/{delivery.id}/status",
        json={"status": "delivered", "otp": delivery_otp.otp},
        headers=auth_headers(runner_user),
    )
    assert correct_response.status_code == 200
    assert correct_response.get_json()["points_earned"] > 0

    reward = RewardPoints.query.filter_by(user_id=runner_user.id).first()
    assert reward is not None
    assert reward.points_balance > 0
