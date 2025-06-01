import pytest
from fastapi.testclient import TestClient
from app import schemas
from app.core.config import settings # For API prefix

API_V1_PREFIX = "/api/v1"

# Test creating a user via API (requires admin for this specific setup in users.py)
# To test this directly, we first need an admin user and their token.
# For simplicity, let's create a utility fixture for an admin token.

@pytest.fixture(scope="module")
def admin_user_token_headers(test_client: TestClient, db_session): # db_session needed by user_service
    from app.services.user_service import UserService
    from app.core.security import create_access_token
    from datetime import timedelta

    # Create admin user directly via service for testing setup
    user_service = UserService(db_session)
    admin_username = "admin_for_test"
    admin_email = "admin_for_test@example.com"
    admin_password = "adminpassword"

    existing_admin = user_service.get_user_by_username(admin_username)
    if not existing_admin:
        admin_user_in = schemas.UserCreate(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            role="admin",
            full_name="Admin Test User"
        )
        user_service.create_user(user_create=admin_user_in)

    # Login admin to get token
    login_data = {"username": admin_username, "password": admin_password}
    response = test_client.post(f"{API_V1_PREFIX}/token/", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    access_token = token_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_create_user_api(test_client: TestClient, admin_user_token_headers: dict):
    user_data = {
        "username": "apiuser",
        "email": "apiuser@example.com",
        "password": "apipassword",
        "full_name": "API Test User",
        "role": "agent"
    }
    response = test_client.post(f"{API_V1_PREFIX}/users/", json=user_data, headers=admin_user_token_headers)
    assert response.status_code == 201, response.text
    created_user = response.json()
    assert created_user["username"] == "apiuser"
    assert created_user["email"] == "apiuser@example.com"
    assert "hashed_password" not in created_user # Ensure password is not returned


def test_login_for_access_token_api(test_client: TestClient, admin_user_token_headers: dict):
    # This user was created by the admin_user_token_headers fixture set up
    # or you can create a specific user for this test then log them in.
    # Here, we'll just test the token endpoint with the admin created for the fixture.
    login_data = {"username": "admin_for_test", "password": "adminpassword"}
    response = test_client.post(f"{API_V1_PREFIX}/token/", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_read_users_me_api(test_client: TestClient, admin_user_token_headers: dict):
    response = test_client.get(f"{API_V1_PREFIX}/users/me", headers=admin_user_token_headers)
    assert response.status_code == 200, response.text
    user_me = response.json()
    assert user_me["username"] == "admin_for_test" # The user associated with the token


def test_read_users_unauthenticated(test_client: TestClient):
    response = test_client.get(f"{API_V1_PREFIX}/users/me")
    assert response.status_code == 401 # Expect unauthorized

# Test creating user with duplicate username via API
def test_create_user_duplicate_username_api(test_client: TestClient, admin_user_token_headers: dict):
    user_data1 = {"username": "api_dup_user", "email": "api_dup1@example.com", "password": "pass", "role": "agent"}
    response1 = test_client.post(f"{API_V1_PREFIX}/users/", json=user_data1, headers=admin_user_token_headers)
    assert response1.status_code == 201

    user_data2 = {"username": "api_dup_user", "email": "api_dup2@example.com", "password": "pass", "role": "agent"}
    response2 = test_client.post(f"{API_V1_PREFIX}/users/", json=user_data2, headers=admin_user_token_headers)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]
