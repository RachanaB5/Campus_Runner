import pytest


@pytest.fixture
def admin_user(make_user):
    return make_user(email="admin@rvu.edu.in", role="admin")


@pytest.fixture
def staff_user(make_user):
    return make_user(email="staff@rvu.edu.in", role="staff")


def test_admin_dashboard_stats(client, admin_user, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    food = make_food()
    make_order(customer=customer, items=[(food, 1, None)], status="confirmed")

    response = client.get("/api/admin/dashboard-stats", headers=auth_headers(admin_user))
    assert response.status_code == 200
    data = response.get_json()
    assert "total_orders" in data
    assert "total_users" in data
    assert data["total_orders"] >= 1
    assert data["total_users"] >= 1


def test_admin_get_all_orders(client, admin_user, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    food = make_food()
    make_order(customer=customer, items=[(food, 2, None)], status="confirmed")

    response = client.get("/api/admin/orders", headers=auth_headers(admin_user))
    assert response.status_code == 200
    orders = response.get_json()["orders"]
    assert len(orders) >= 1


def test_admin_get_orders_filtered_by_status(client, admin_user, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    food = make_food()
    make_order(customer=customer, items=[(food, 1, None)], status="confirmed")
    make_order(customer=customer, items=[(food, 1, None)], status="delivered", delivery_status="delivered")

    confirmed = client.get("/api/admin/orders?status=confirmed", headers=auth_headers(admin_user))
    assert confirmed.status_code == 200
    assert all(o["status"] == "confirmed" for o in confirmed.get_json()["orders"])


def test_admin_get_all_users(client, admin_user, make_user, auth_headers):
    make_user(email="student1@rvu.edu.in")
    make_user(email="student2@rvu.edu.in")

    response = client.get("/api/admin/users", headers=auth_headers(admin_user))
    assert response.status_code == 200
    users = response.get_json()["users"]
    assert len(users) >= 2


def test_admin_update_user_role(client, admin_user, make_user, auth_headers):
    target = make_user(email="target@rvu.edu.in", role="customer")

    response = client.put(
        f"/api/admin/user/{target.id}/update-role",
        json={"role": "staff"},
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200

    from models import User
    updated = User.query.get(target.id)
    assert updated.role == "staff"


def test_admin_toggle_food_availability(client, admin_user, make_food, auth_headers):
    food = make_food(available=True)

    response = client.post(
        f"/api/admin/food/{food.id}/toggle-availability",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200

    from models import Food
    toggled = Food.query.get(food.id)
    assert toggled.available is False


def test_non_admin_cannot_access_admin_routes(client, make_user, auth_headers):
    regular = make_user(email="regular@rvu.edu.in", role="customer")
    response = client.get("/api/admin/dashboard-stats", headers=auth_headers(regular))
    assert response.status_code == 403


def test_staff_can_view_orders(client, staff_user, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    food = make_food()
    make_order(customer=customer, items=[(food, 1, None)])

    response = client.get("/api/admin/orders", headers=auth_headers(staff_user))
    assert response.status_code == 200
