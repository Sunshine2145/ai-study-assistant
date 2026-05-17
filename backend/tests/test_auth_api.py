"""Authentication API unit tests."""

import hashlib

from src.routes.auth import (
    generate_verification_code,
    hash_password,
    verification_codes,
)


class TestAuthHelpers:
    def test_hash_password_is_sha256_hex(self):
        result = hash_password("secret123")
        expected = hashlib.sha256(b"secret123").hexdigest()
        assert result == expected
        assert len(result) == 64

    def test_generate_verification_code_length(self):
        code = generate_verification_code(6)
        assert len(code) == 6
        assert code.isdigit()


class TestAuthAPI:
    def test_register_success(self, client, unique_username):
        resp = client.post(
            "/api/auth/register",
            json={"username": unique_username, "password": "Pass123!", "nickname": "新用户"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == unique_username
        assert data["role"] == "user"
        assert "token" in data
        assert data["user_id"] > 0

    def test_register_duplicate_username(self, client, registered_user):
        resp = client.post(
            "/api/auth/register",
            json={"username": registered_user["username"], "password": "OtherPass1"},
        )
        assert resp.status_code == 400
        assert "已存在" in resp.json()["detail"]

    def test_login_success(self, client, registered_user):
        resp = client.post(
            "/api/auth/login",
            json={
                "username": registered_user["username"],
                "password": registered_user["password"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == registered_user["username"]
        assert isinstance(data["permissions"], list)
        assert "token" in data

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post(
            "/api/auth/login",
            json={"username": registered_user["username"], "password": "WrongPassword"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"username": "no_such_user_xyz", "password": "any"},
        )
        assert resp.status_code == 401

    def test_get_me_returns_user_shape(self, client, registered_user):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "nickname" in data
        assert "score" in data

    def test_get_current_user_full(self, client, registered_user):
        resp = client.get("/api/auth/current")
        assert resp.status_code == 200
        data = resp.json()
        assert "username" in data
        assert "role" in data
        assert "permissions" in data

    def test_send_and_login_with_code(self, client, registered_user):
        username = registered_user["username"]
        verification_codes.clear()

        send_resp = client.post("/api/auth/send-code", json={"username": username})
        assert send_resp.status_code == 200
        assert send_resp.json()["success"] is True

        stored = verification_codes[username]["code"]
        login_resp = client.post(
            "/api/auth/login-code",
            json={"username": username, "code": stored},
        )
        assert login_resp.status_code == 200
        assert login_resp.json()["username"] == username

    def test_login_code_invalid(self, client, registered_user):
        username = registered_user["username"]
        verification_codes.clear()
        client.post("/api/auth/send-code", json={"username": username})

        resp = client.post(
            "/api/auth/login-code",
            json={"username": username, "code": "000000"},
        )
        assert resp.status_code == 400
