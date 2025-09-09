import pytest
from fastapi.testclient import TestClient
from convergent.main import app

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from convergent.database import Base, get_db
from convergent.models import *
from uuid import uuid4

import logging

logging.basicConfig(level=logging.INFO)

test_engine = create_engine("sqlite:///./test.db" , connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def register_user(client: TestClient):
    def _register(username: str, password: str):
        payload = {
            "username": username,
            "password": password,
        }
        response = client.post("/register", json=payload)
        return response
    return _register

@pytest.fixture(scope="function")
def unique_token(client: TestClient):
    username = f"testuser{uuid4()}"
    password = "securepassword"
    payload = {
        "username": username,
        "password": password,
    }
    client.post("/register", json=payload)
    
    response = client.post("/token", data=payload)
    token = response.json().get("access_token")
    
    yield token

@pytest.fixture(scope="function")
def create_token(client: TestClient):
    def _create_token(username: str):
        password = "securepassword"
        payload = {
            "username": username,
            "password": password,
        }
        client.post("/register", json=payload)
        
        response = client.post("/token", data=payload)
        token = response.json().get("access_token")
        
        return token
    return _create_token

@pytest.fixture(scope="function")
def authenticated_client(client: TestClient, unique_token):
    client.cookies.set("access_token", unique_token)
    yield client

@pytest.fixture(scope="function")
def authenticated_clients(db, create_token):
    def _create_clients(num_users):
        clients = {}

        def override_get_db():
            try:
                yield db
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        for i in range(num_users):
            username = f"user{i+1}"
            token = create_token(username)

            test_client = TestClient(app)
            test_client.cookies.set("access_token", token)

            clients[username] = test_client
        
        return clients
    yield _create_clients

@pytest.fixture(scope="function")
def valid_conversation_data(
    name=f"Test Conversation {uuid4()}", 
    description="This is a test conversation.", 
    user_friendly_link=None,
    is_active=True,
    display_unmoderated=True
):
    return {
        "name": name,
        "description": description,
        "user_friendly_link": user_friendly_link,
        "is_active": is_active,
        "display_unmoderated": display_unmoderated,
    }

@pytest.fixture(scope="function")
def create_conversation( 
    valid_conversation_data,
    authenticated_clients,
):
    default_client = authenticated_clients(1)["user1"]
    
    def _create(
        authenticated_client: TestClient = None,
        extra_data: dict = None
    ):
        client = authenticated_client or default_client

        data = valid_conversation_data.copy()
        if extra_data:
            data.update(extra_data)
            
        response = client.post("/conversations",json=data,)
        return response
    return _create

@pytest.fixture(scope="function")
def create_comment():
    def _create(
        client: TestClient, 
        conversation_id: str, 
        content: str = "This is a test comment."
    ):
        response = client.post(
            f"/conversations/{conversation_id}/comments",
            json={"content": content},
        )
        return response
    return _create

@pytest.fixture(scope="function")
def approve_comment():
    def _approve(
        client: TestClient, 
        comment_id: str
    ):
        response = client.put(
            f"/moderation/comments/{comment_id}/approve"
        )
        return response
    return _approve

@pytest.fixture(scope="function")
def reject_comment():
    def _reject(
        client: TestClient, 
        comment_id: str
    ):
        response = client.put(
            f"/moderation/comments/{comment_id}/reject"
        )
        return response
    return _reject

@pytest.fixture(scope="function")
def vote_on_comment():
    def _vote(
        client: TestClient, 
        comment_id: str, 
        value: int
    ):
        response = client.post(
            f"/comments/{comment_id}/vote",
            json={"value": value},
        )
        return response
    return _vote