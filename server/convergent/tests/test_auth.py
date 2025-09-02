import random
import string
from convergent.models import User

def generate_random_username(length=8):
    # Generate a random string of letters and digits of the given length
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class TestRegister:
    def test_register_success(self, client, db):
        """
        Test successful user registration
        Expected behaviour:
        - The API should return a 200 status code
        - The response should contain the registered username
        - The user should be stored in the database with a hashed password
        """
        username = generate_random_username()
        response = client.post("/register", json={"username": username, "password": "securepass"})
        
        assert response.status_code == 200
        assert response.json() == {"username": username}

        # Verify that the user is actually in the database
        user = db.query(User).filter_by(username=username).first()
        assert user is not None
        assert user.hashed_password != "securepass" 


    def test_register_duplicate_username(self, client, db):
        """
        Test registration with a username that already exists
        Expected behaviour:
        - The API should return a 409 status code
        - The response should indicate that the username already exists
        """
        # Setup: register the first user
        response1 = client.post("/register", json={"username": "user1", "password": "pass"})
        assert response1.status_code == 200
        
        # Test: register same username again
        response2 = client.post("/register", json={"username": "user1", "password": "pass2"})
        assert response2.status_code == 409
        assert response2.json()["detail"] == "Username already exists"


    def test_register_missing_username(self, client):
        """
        Test registration with missing username
        Expected behaviour:
        - The API should return a 422 status code
        """
        response = client.post("/register", json={"password": "securepass"})
        assert response.status_code == 422


    def test_register_missing_password(self, client):
        """
        Test registration with missing password
        Expected behaviour:
        - The API should return a 422 status code
        """
        username = generate_random_username()

        response = client.post("/register", json={"username": username})
        assert response.status_code == 422


class TestToken:
    def test_token_success(self, client, register_user):
        """
        Test successful token retrieval
        Expected behaviour:
        - The API should return a 200 status code
        - The response should contain an access token and token type
        - The response should set a cookie with the access token
        - The access token should work for accessing a protected endpoint
        """
        username = generate_random_username()
        password = "securepassword"
        register_user(username, password)

        # Request a token
        response = client.post("/token", data={"username": username, "password": password})       
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
        assert "set-cookie" in response.headers

        # Verify that the token works by accessing a protected endpoint
        client.cookies.set("access_token", response.json()["access_token"])
        me_response = client.get("/users/me")
        assert me_response.status_code == 200
        assert me_response.json() == {"username": username}


    def test_token_nonexistent_user(self, client):
        """
        Test token retrieval with a username that does not exist
        Expected behaviour:
        - The API should return a 401 status code
        - The response should indicate that the username or password is incorrect
        """
        username = "nonexistentuser"
        password = "wrongpassword"
        
        response = client.post("/token", data={"username": username, "password": password})
        assert response.status_code == 401
        assert response.json() == {"detail": "Incorrect username or password"}


    def test_token_incorrect_password(self, client, register_user):
        """
        Test token retrieval with an incorrect password
        Expected behaviour:
        - The API should return a 401 status code
        - The response should indicate that the username or password is incorrect
        """
        username = generate_random_username()
        password = "securepassword"
        register_user(username, password)

        response = client.post("/token", data={"username": username, "password": "wrongpassword"})        
        assert response.status_code == 401
    

    def test_login_missing_username(self, client):
        """
        Test token retrieval with missing username
        Expected behaviour:
        - The API should return a 422 status code
        """

        response = client.post("/token", data={"password": "securepassword"})
        assert response.status_code == 422


    def test_login_missing_password(self, client):
        """
        Test token retrieval with missing password
        Expected behaviour:
        - The API should return a 422 status code
        """
        username = "validuser"

        response = client.post("/token", data={"username": username})
        assert response.status_code == 422


class TestUsersMe:
    def test_read_users_me_success(self, authenticated_clients):
        """
        Test accessing the /users/me endpoint with a valid token
        Expected behaviour:
        - The API should return a 200 status code
        - The response should contain the authenticated user's username
        """
        clients = authenticated_clients(1)
        authenticated_client = clients["user1"]
        
        response = authenticated_client.get("/users/me")
        assert response.status_code == 200
        assert response.json() == {"username": "user1"}


    def test_read_users_me_no_token(self, client):
        """
        Test accessing the /users/me endpoint without a token
        Expected behaviour:
        - The API should return a 422 status code
        """
        client.cookies.clear()
        response = client.get("/users/me")
        assert response.status_code == 422
    

    def test_read_users_me_invalid_token(self, client):
        """
        Test accessing the /users/me endpoint with an invalid token
        Expected behaviour:
        - The API should return a 401 status code
        """
        client.cookies.set("access_token", "invalidtoken")
        response = client.get("/users/me")
        assert response.status_code == 401


class TestLogOut:
    def test_logout_with_token(self, authenticated_clients):
        """
        Test logging out with a valid token
        Expected behaviour:
        - The API should return a 200 status code
        - The response should indicate successful logout
        """
        authenticated_client = authenticated_clients(1)["user1"]
        response = authenticated_client.get("/users/me")
        assert response.status_code == 200
        
        response = authenticated_client.post("/logout")
        assert response.status_code == 200
        assert response.json() == {"message": "Logged out"}
        assert "access_token" not in response.cookies
    

    def test_logout_no_token(self, client):
        """
        Test the logging out endpoint when client is not logged in
        Expected behaviour:
        - The API should return a 200 status code
        - The response should indicate successful logout
        """
        client.cookies.clear()

        response = client.post("/logout")
        assert response.status_code == 200
        assert response.json() == {"message": "Logged out"}
        assert "access_token" not in response.cookies
