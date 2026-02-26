def signup_and_token(client, name, email):
    r = client.post(
        "/api/auth/signup",
        json={"name": name, "email": email, "password": "pass123"},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_maintainer_can_change_assignee_but_member_cannot(client):
    maintainer_token = signup_and_token(client, "Maintainer", "maintainer@example.com")
    member_token = signup_and_token(client, "Member", "member@example.com")
    maintainer_id = client.get("/api/me", headers=auth_headers(maintainer_token)).json()["id"]
    member_id = client.get("/api/me", headers=auth_headers(member_token)).json()["id"]

    proj = client.post(
        "/api/projects",
        headers=auth_headers(maintainer_token),
        json={"name": "Proj", "key": "PRJ1", "description": "x"},
    )
    project_id = proj.json()["id"]

    client.post(
        f"/api/projects/{project_id}/members",
        headers=auth_headers(maintainer_token),
        json={"email": "member@example.com", "role": "member"},
    )

    forbidden_create = client.post(
        f"/api/projects/{project_id}/issues",
        headers=auth_headers(member_token),
        json={"title": "Need assign", "description": "d", "priority": "medium"},
    )
    assert forbidden_create.status_code == 403

    issue = client.post(
        f"/api/projects/{project_id}/issues",
        headers=auth_headers(maintainer_token),
        json={"title": "Need assign", "description": "d", "priority": "medium"},
    )
    assert issue.status_code == 200
    issue_id = issue.json()["id"]

    forbidden = client.patch(
        f"/api/issues/{issue_id}",
        headers=auth_headers(member_token),
        json={"assignee_id": maintainer_id},
    )
    assert forbidden.status_code == 403

    ok = client.patch(
        f"/api/issues/{issue_id}",
        headers=auth_headers(maintainer_token),
        json={"assignee_id": member_id, "status": "in_progress"},
    )
    assert ok.status_code == 200
    assert ok.json()["assignee_id"] == member_id
    assert ok.json()["status"] == "in_progress"


def test_issue_filter_and_pagination(client):
    token = signup_and_token(client, "Alice", "alicef@example.com")
    proj = client.post(
        "/api/projects",
        headers=auth_headers(token),
        json={"name": "Filters", "key": "FLT1", "description": "x"},
    )
    project_id = proj.json()["id"]

    payloads = [
        {"title": "alpha bug", "priority": "high"},
        {"title": "alpha feature", "priority": "low"},
        {"title": "beta bug", "priority": "high"},
    ]
    for p in payloads:
        client.post(
            f"/api/projects/{project_id}/issues",
            headers=auth_headers(token),
            json={"title": p["title"], "priority": p["priority"]},
        )

    result = client.get(
        f"/api/projects/{project_id}/issues?q=alpha&priority=high&limit=2&offset=0",
        headers=auth_headers(token),
    )
    assert result.status_code == 200
    data = result.json()
    assert len(data) == 1
    assert data[0]["title"] == "alpha bug"


def test_member_role_management_endpoints(client):
    maintainer_token = signup_and_token(client, "Owner", "owner@example.com")
    other_token = signup_and_token(client, "Other", "other@example.com")

    proj = client.post(
        "/api/projects",
        headers=auth_headers(maintainer_token),
        json={"name": "Members", "key": "MEM1", "description": "x"},
    )
    project_id = proj.json()["id"]

    add = client.post(
        f"/api/projects/{project_id}/members",
        headers=auth_headers(maintainer_token),
        json={"email": "other@example.com", "role": "member"},
    )
    assert add.status_code == 200

    members = client.get(f"/api/projects/{project_id}/members", headers=auth_headers(other_token))
    assert members.status_code == 200
    user_id = [m["user_id"] for m in members.json() if m["email"] == "other@example.com"][0]

    promote = client.patch(
        f"/api/projects/{project_id}/members/{user_id}",
        headers=auth_headers(maintainer_token),
        json={"role": "maintainer"},
    )
    assert promote.status_code == 200

    remove = client.delete(
        f"/api/projects/{project_id}/members/{user_id}",
        headers=auth_headers(maintainer_token),
    )
    assert remove.status_code == 200


def test_maintained_projects_and_onboard_member(client):
    maintainer_token = signup_and_token(client, "Owner2", "owner2@example.com")
    member_token = signup_and_token(client, "User2", "user2@example.com")

    proj = client.post(
        "/api/projects",
        headers=auth_headers(maintainer_token),
        json={"name": "TeamOps", "key": "TOP1", "description": "x"},
    )
    project_id = proj.json()["id"]

    # add member to project, but they are not maintainer
    client.post(
        f"/api/projects/{project_id}/members",
        headers=auth_headers(maintainer_token),
        json={"email": "user2@example.com", "role": "member"},
    )

    maintained_by_owner = client.get("/api/projects/maintained", headers=auth_headers(maintainer_token))
    assert maintained_by_owner.status_code == 200
    assert len(maintained_by_owner.json()) == 1

    maintained_by_member = client.get("/api/projects/maintained", headers=auth_headers(member_token))
    assert maintained_by_member.status_code == 200
    assert len(maintained_by_member.json()) == 0

    forbidden = client.post(
        f"/api/projects/{project_id}/members/onboard",
        headers=auth_headers(member_token),
        json={"name": "New User", "email": "newuser@example.com", "password": "pass123", "role": "member"},
    )
    assert forbidden.status_code == 403

    onboard = client.post(
        f"/api/projects/{project_id}/members/onboard",
        headers=auth_headers(maintainer_token),
        json={"name": "New User", "email": "newuser@example.com", "password": "pass123", "role": "member"},
    )
    assert onboard.status_code == 200
