def test_cart_add_update_and_clear(client, make_user, make_food, auth_headers):
    user = make_user(email="cart@rvu.edu.in")
    food = make_food(name="Veg Burger", price=70)

    add_response = client.post("/api/cart/add", json={
        "food_id": food.id,
        "quantity": 2,
        "customizations": "Spice level: Mild",
    }, headers=auth_headers(user))
    assert add_response.status_code == 200
    cart = add_response.get_json()["cart"]
    assert cart["item_count"] == 2
    item_id = cart["items"][0]["id"]

    update_response = client.put(f"/api/cart/item/{item_id}", json={
        "quantity": 3,
        "customizations": "Spice level: Spicy",
    }, headers=auth_headers(user))
    assert update_response.status_code == 200
    updated_cart = update_response.get_json()["cart"]
    assert updated_cart["item_count"] == 3
    assert updated_cart["items"][0]["customizations"] == "Spice level: Spicy"

    clear_response = client.delete("/api/cart/clear", headers=auth_headers(user))
    assert clear_response.status_code == 200
    assert clear_response.get_json()["cart"]["item_count"] == 0


def test_checkout_creates_order_delivery_and_otps(client, make_user, make_food, auth_headers):
    user = make_user(email="checkout@rvu.edu.in")
    food = make_food(name="Chicken Burger", price=90, is_veg=False)

    response = client.post("/api/checkout", json={
        "items": [
            {"food_id": food.id, "quantity": 2, "price": 90, "customizations": "Spice level: Medium"}
        ],
        "delivery_address": "Hostel B, Room 214",
        "delivery_city": "Bangalore",
        "delivery_pincode": "560001",
        "customer_phone": "9876543210",
        "payment_method": "cod",
        "subtotal": 180,
        "tax_amount": 9,
        "delivery_fee": 10,
        "final_total": 199,
        "special_instructions": "Ring the bell once",
    }, headers=auth_headers(user))

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["order_id"]
    assert len(payload["pickup_otp"]) == 4
    assert len(payload["delivery_otp"]) == 4


def test_order_tracking_returns_otps_for_owner(client, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="tracking@rvu.edu.in")
    food = make_food()
    order, _delivery = make_order(
        customer=customer,
        items=[(food, 1, None)],
        status="confirmed",
        delivery_status="assigned",
        create_otps=True,
    )

    response = client.get(f"/api/orders/{order.id}/track", headers=auth_headers(customer))
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["delivery_otp"]
    assert payload["pickup_otp"]
    assert payload["timeline"][0]["status"] == "placed"


def test_my_orders_flags_unreviewed_delivered_items(client, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="orders@rvu.edu.in")
    food = make_food()
    make_order(customer=customer, items=[(food, 1, None)], status="delivered", delivery_status="delivered")

    response = client.get("/api/orders/my-orders", headers=auth_headers(customer))
    assert response.status_code == 200
    order_payload = response.get_json()["orders"][0]
    assert order_payload["has_unreviewed_items"] is True
    assert len(order_payload["reviewable_items"]) == 1
