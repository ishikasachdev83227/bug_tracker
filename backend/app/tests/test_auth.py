def test_signup_and_login(client):
    r = client.post("/api/auth/signup", json={"name": "Alice", "email": "alice@example.com", "password": "pass123"})
    assert r.status_code == 200
    token = r.json().get("access_token")
    assert token

    r2 = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "pass123"})
    assert r2.status_code == 200
    assert r2.json().get("access_token")
