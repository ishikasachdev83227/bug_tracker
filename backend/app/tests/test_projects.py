def test_create_project_requires_auth(client):
    r = client.post("/api/projects", json={"name": "Test", "key": "TST", "description": "x"})
    assert r.status_code in (401, 403)
