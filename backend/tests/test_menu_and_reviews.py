import uuid


def test_menu_all_and_food_detail_include_reviews(client, make_food, make_user):
    from models import Review, db

    food = make_food(name="Paneer Burger", category="Burgers", price=80)
    reviewer = make_user(email="reviewer@rvu.edu.in")
    db.session.add_all([
        Review(id=str(uuid.uuid4()), user_id=reviewer.id, food_id=food.id, rating=5, comment="Amazing", is_seeded=True, seeded_name="Campus Foodie"),
        Review(id=str(uuid.uuid4()), user_id=reviewer.id, food_id=food.id, rating=4, comment="Pretty good", is_seeded=True, seeded_name="Campus Bites"),
    ])
    food.rating = 4.5
    food.review_count = 2
    db.session.commit()

    all_response = client.get("/api/menu/all")
    assert all_response.status_code == 200
    assert any(item["id"] == food.id for item in all_response.get_json()["foods"])

    detail_response = client.get(f"/api/menu/{food.id}")
    assert detail_response.status_code == 200
    detail = detail_response.get_json()
    assert detail["rating_count"] == 2
    assert detail["rating_distribution"]["5"] == 1
    assert len(detail["reviews"]) == 2


def test_menu_search_and_category_alias(client, make_food):
    make_food(name="Chicken Hyderabadi Biryani", category="Biryanis", price=140, is_veg=False)

    search_response = client.get("/api/menu/search?q=hyderabadi")
    assert search_response.status_code == 200
    assert len(search_response.get_json()["foods"]) == 1

    category_response = client.get("/api/menu/category/biryani")
    assert category_response.status_code == 200
    assert len(category_response.get_json()["foods"]) == 1


def test_submit_review_requires_delivered_order(client, make_user, make_food, make_order, auth_headers):
    customer = make_user(email="customer@rvu.edu.in")
    food = make_food()
    order, _delivery = make_order(customer=customer, items=[(food, 1, None)], status="confirmed")

    response = client.post("/api/reviews", json={
        "order_id": order.id,
        "food_id": food.id,
        "rating": 5,
        "comment": "Should not work",
    }, headers=auth_headers(customer))

    assert response.status_code == 403


def test_submit_review_recalculates_rating(client, make_user, make_food, make_order, auth_headers):
    from models import Review, db

    customer = make_user(email="customer@rvu.edu.in")
    other_user = make_user(email="seed@rvu.edu.in")
    food = make_food(name="Masala Dosa", category="South Indian", price=60)

    db.session.add_all([
        Review(id=str(uuid.uuid4()), user_id=other_user.id, food_id=food.id, rating=4, comment="Nice", is_seeded=True, seeded_name="Campus Foodie"),
        Review(id=str(uuid.uuid4()), user_id=other_user.id, food_id=food.id, rating=5, comment="Loved it", is_seeded=True, seeded_name="Hostel Eats"),
    ])
    food.rating = 4.5
    food.review_count = 2
    db.session.commit()

    order, _delivery = make_order(customer=customer, items=[(food, 1, "Spice level: Medium")], status="delivered", delivery_status="delivered")
    response = client.post("/api/reviews", json={
        "order_id": order.id,
        "food_id": food.id,
        "rating": 5,
        "comment": "Amazing as always",
    }, headers=auth_headers(customer))

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["rating_count"] == 3
    assert payload["new_rating"] == 4.7


def test_reviewable_items_only_returns_unreviewed_delivered_items(client, make_user, make_food, make_order, auth_headers):
    from models import Review, db

    customer = make_user(email="customer@rvu.edu.in")
    food_one = make_food(name="Item One")
    food_two = make_food(name="Item Two")
    order, _delivery = make_order(
        customer=customer,
        items=[(food_one, 1, None), (food_two, 2, None)],
        status="delivered",
        delivery_status="delivered",
    )

    db.session.add(Review(
        id=str(uuid.uuid4()),
        user_id=customer.id,
        food_id=food_one.id,
        order_id=order.id,
        rating=4,
        comment="Already reviewed",
    ))
    db.session.commit()

    response = client.get(f"/api/orders/{order.id}/reviewable-items", headers=auth_headers(customer))
    assert response.status_code == 200
    items = response.get_json()["items"]
    assert len(items) == 1
    assert items[0]["food_id"] == food_two.id
