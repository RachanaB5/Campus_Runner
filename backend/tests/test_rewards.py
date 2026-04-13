def test_rewards_balance_starts_at_zero(client, make_user, auth_headers):
    user = make_user(email="rewards@rvu.edu.in")
    response = client.get("/api/rewards/my-points", headers=auth_headers(user))
    assert response.status_code == 200
    data = response.get_json()
    assert data["points_balance"] == 0
    assert data["total_points"] == 0
    assert data["tier"] == "bronze"


def test_rewards_earned_after_delivery(client, make_user, make_runner, make_food, make_order, auth_headers):
    from models import OrderOTP, RewardPoints

    customer = make_user(email="customer@rvu.edu.in")
    runner_user, _runner = make_runner(email="runner@rvu.edu.in")
    food = make_food(name="Veg Burger", price=80)
    order, delivery = make_order(
        customer=customer,
        items=[(food, 1, None)],
        status="confirmed",
        delivery_status="assigned",
        create_otps=True,
        runner_user_id=runner_user.id,
    )

    client.put(
        f"/api/runner/delivery/{delivery.id}/status",
        json={"status": "picked_up"},
        headers=auth_headers(runner_user),
    )

    otp = OrderOTP.query.filter_by(order_id=order.id, otp_type="delivery").first()
    client.put(
        f"/api/runner/delivery/{delivery.id}/status",
        json={"status": "delivered", "otp": otp.otp},
        headers=auth_headers(runner_user),
    )

    reward = RewardPoints.query.filter_by(user_id=runner_user.id).first()
    assert reward.points_balance > 0
    assert reward.total_points > 0


def test_rewards_transactions_list(client, make_user, make_runner, make_food, make_order, auth_headers):
    from models import OrderOTP

    customer = make_user(email="customer@rvu.edu.in")
    runner_user, _runner = make_runner(email="runner@rvu.edu.in")
    food = make_food(price=100)
    order, delivery = make_order(
        customer=customer,
        items=[(food, 1, None)],
        status="confirmed",
        delivery_status="assigned",
        create_otps=True,
        runner_user_id=runner_user.id,
    )

    client.put(
        f"/api/runner/delivery/{delivery.id}/status",
        json={"status": "picked_up"},
        headers=auth_headers(runner_user),
    )
    otp = OrderOTP.query.filter_by(order_id=order.id, otp_type="delivery").first()
    client.put(
        f"/api/runner/delivery/{delivery.id}/status",
        json={"status": "delivered", "otp": otp.otp},
        headers=auth_headers(runner_user),
    )

    response = client.get("/api/rewards/transactions", headers=auth_headers(runner_user))
    assert response.status_code == 200
    transactions = response.get_json()["transactions"]
    assert len(transactions) >= 1
    assert transactions[0]["type"] == "earned"
    assert transactions[0]["points"] > 0


def test_rewards_requires_auth(client):
    response = client.get("/api/rewards/my-points")
    assert response.status_code == 401
