def test_add_upi_payment_method(client, make_user, auth_headers):
    user = make_user(email="upi@rvu.edu.in")

    response = client.post("/api/payment-methods", json={
        "type": "upi",
        "upi_id": "student@okaxis",
        "upi_nickname": "My GPay",
        "is_default": True,
    }, headers=auth_headers(user))

    assert response.status_code == 201
    method = response.get_json()["payment_method"]
    assert method["type"] == "upi"
    assert method["upi_id"] == "student@okaxis"
    assert method["is_default"] is True


def test_add_card_payment_method_hashes_card_number(client, make_user, auth_headers):
    from models import SavedPaymentMethod

    user = make_user(email="card@rvu.edu.in")

    response = client.post("/api/payment-methods", json={
        "type": "card",
        "card_number": "4111111111111111",
        "card_holder_name": "Campus Runner",
        "card_expiry": "08/2030",
        "card_pin": "1234",
        "is_default": True,
    }, headers=auth_headers(user))

    assert response.status_code == 201
    payload = response.get_json()["payment_method"]
    assert payload["card_last4"] == "1111"
    assert payload["card_brand"] == "Visa"

    saved = SavedPaymentMethod.query.filter_by(user_id=user.id).first()
    assert saved.card_number_hash
    assert "4111111111111111" not in saved.card_number_hash


def test_set_default_and_delete_payment_method(client, make_user, auth_headers):
    user = make_user(email="methods@rvu.edu.in")

    first = client.post("/api/payment-methods", json={
        "type": "upi",
        "upi_id": "first@okaxis",
        "upi_nickname": "First",
    }, headers=auth_headers(user)).get_json()["payment_method"]
    second = client.post("/api/payment-methods", json={
        "type": "upi",
        "upi_id": "second@okaxis",
        "upi_nickname": "Second",
    }, headers=auth_headers(user)).get_json()["payment_method"]

    default_response = client.put(f"/api/payment-methods/{second['id']}/default", headers=auth_headers(user))
    assert default_response.status_code == 200

    list_response = client.get("/api/payment-methods", headers=auth_headers(user))
    methods = list_response.get_json()["payment_methods"]
    assert methods[0]["id"] == second["id"]
    assert methods[0]["is_default"] is True

    delete_response = client.delete(f"/api/payment-methods/{first['id']}", headers=auth_headers(user))
    assert delete_response.status_code == 200
    methods_after_delete = client.get("/api/payment-methods", headers=auth_headers(user)).get_json()["payment_methods"]
    assert len(methods_after_delete) == 1
