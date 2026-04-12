def test_register_creates_unverified_user_and_otp(client):
    import routes.auth_routes as auth_routes
    from models import User

    response = client.post("/api/auth/signup", json={
        "name": "Aarav Test",
        "email": "aarav@rvu.edu.in",
        "password": "secret123",
        "phone": "9876543210",
    })

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["access_token"]
    assert payload["user"]["is_verified"] is False

    user = User.query.filter_by(email="aarav@rvu.edu.in").first()
    assert user is not None
    assert "aarav@rvu.edu.in" in auth_routes.otp_store


def test_verify_otp_marks_user_verified(client):
    import routes.auth_routes as auth_routes
    from models import User

    client.post("/api/auth/signup", json={
        "name": "Aarav Test",
        "email": "aarav@rvu.edu.in",
        "password": "secret123",
    })
    otp_code = auth_routes.otp_store["aarav@rvu.edu.in"]["otp"]

    response = client.post("/api/auth/verify-otp", json={
        "email": "aarav@rvu.edu.in",
        "otp": otp_code,
    })

    assert response.status_code == 200
    user = User.query.filter_by(email="aarav@rvu.edu.in").first()
    assert user.is_verified is True


def test_login_rejects_wrong_password(client, make_user):
    make_user(email="login@rvu.edu.in", password="correct123")

    response = client.post("/api/auth/login", json={
        "email": "login@rvu.edu.in",
        "password": "wrong123",
    })

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid email or password"


def test_profile_update_and_change_password(client, make_user, auth_headers):
    user = make_user(name="Before Name", email="profile@rvu.edu.in", password="oldpass123", phone="9999999999")

    update_response = client.put(
        "/api/auth/profile",
        json={"name": "After Name", "phone": "1234567890"},
        headers=auth_headers(user),
    )
    assert update_response.status_code == 200
    updated_user = update_response.get_json()["user"]
    assert updated_user["name"] == "After Name"
    assert updated_user["phone"] == "1234567890"

    password_response = client.put(
        "/api/auth/change-password",
        json={
            "current_password": "oldpass123",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        },
        headers=auth_headers(user),
    )
    assert password_response.status_code == 200

    login_response = client.post("/api/auth/login", json={
        "email": "profile@rvu.edu.in",
        "password": "newpass123",
    })
    assert login_response.status_code == 200


def test_auth_me_returns_real_stats(client, make_user, make_runner, make_food, make_order, auth_headers):
    customer = make_user(email="stats@rvu.edu.in")
    make_runner(email="stats-runner@rvu.edu.in")
    food = make_food()
    make_order(
        customer=customer,
        items=[(food, 2, None)],
        status="delivered",
        delivery_status="delivered",
    )

    response = client.get("/api/auth/me", headers=auth_headers(customer))
    assert response.status_code == 200
    stats = response.get_json()["stats"]
    assert stats["total_orders"] == 1
    assert "total_points" in stats
    assert "deliveries_made" in stats
