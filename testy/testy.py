def login_token(client, username: str, password: str) -> str:
    r = client.post("/login", data={"username": username, "password": password})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    return body["access_token"]



def test_login_success(client):
    r = client.post("/login", data={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_bad_credentials(client):
    r = client.post("/login", data={"username": "admin", "password": "123"})
    assert r.status_code == 401
    assert "detail" in r.json()



def test_user_details_no_token(client):
    r = client.get("/user_details")
    assert r.status_code == 401


def test_user_details_ok(client):
    token = login_token(client, "user", "user123")
    r = client.get("/user_details", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "user"
    assert "ROLE_USER" in data["roles"]



def test_create_user_forbidden_for_non_admin(client):
    token = login_token(client, "user", "user123")
    r = client.post(
        "/users",
        json={"username": "new1", "password": "pass", "roles": ["ROLE_USER"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403
    assert "detail" in r.json()


def test_create_user_ok_for_admin(client):
    token = login_token(client, "admin", "admin123")
    r = client.post(
        "/users",
        json={"username": "new2", "password": "pass", "roles": ["ROLE_USER"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "new2"
    assert "ROLE_USER" in data["roles"]

    r2 = client.post("/login", data={"username": "new2", "password": "pass"})
    assert r2.status_code == 200
    assert "access_token" in r2.json()
