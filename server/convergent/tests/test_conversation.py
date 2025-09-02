from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import pytest
from convergent.models import Conversation, Comment



class UserBasic(BaseModel):
    id: UUID
    username: str

class ConversationResponse(BaseModel):
    id: UUID
    name: str
    description: str = None
    author: UserBasic
    num_participants: int = None
    display_unmoderated: bool
    date_created: datetime = None
    is_active: bool = True
    user_friendly_link: Optional[str] = None

    model_config = ConfigDict(extra='forbid')

class CommentResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    user_id: UUID
    content: str
    approved: bool
    date_created: datetime

    model_config = ConfigDict(extra='forbid')

class RemainingCommentResponse(BaseModel):
    num_votes: int
    comment: CommentResponse

    model_config = ConfigDict(extra='forbid')



class TestCreateConversation:
    def test_create_conversation_success(self, db, authenticated_clients, valid_conversation_data):
        """
        Test the successful creation of a conversation when a user is logged in
        Expected Behavior:
        - The API returns a 200 status code
        - The response JSON contains an "id" field with the new conversation ID
        """
        authenticated_client = authenticated_clients(1)["user1"]
        
        response = authenticated_client.post(
            "/conversations",
            json=valid_conversation_data,
        )
        assert response.status_code == 200
        assert "id" in response.json()

        # Verify the conversation is in the database
        conversation_id = UUID(response.json()["id"])
        conversation_in_db = db.query(Conversation).filter_by(id=conversation_id).first()
        assert conversation_in_db is not None
        assert conversation_in_db.name == valid_conversation_data["name"]
    

    def test_create_conversation_missing_cookie(self, client, valid_conversation_data):
        """
        Test handling an unauthenticated user attempting to create a conversation
        Expected Behavior:
        - The API returns a 422 status code
        """
        client.cookies.clear()

        response = client.post("/conversations", json=valid_conversation_data)
        assert response.status_code == 422


    def test_create_conversation_missing_fields(self, authenticated_clients): 
        """
        Test handling of a missing field (in this case the "name" field)
        Expected Behavior:
        - The API returns a 422 status code
        """
        authenticated_client = authenticated_clients(1)["user1"]
        invalid_data = {
            "description": "This is a test conversation."  # Missing 'name'
        }

        response = authenticated_client.post(
            "/conversations",
            json=invalid_data
        )
        assert response.status_code == 422


    def test_create_conversation_normalizes_link(self, db, authenticated_clients, valid_conversation_data):
        """
        Test link normalization when user provides an optional user-friendly link
        Expected Behavior:
        - The API returns a 200 status code
        - The link stored in the database is a normalized version of the provided string
        """
        authenticated_client = authenticated_clients(1)["user1"]
        valid_conversation_data["user_friendly_link"] = "  Test Convo Link  "
        response = authenticated_client.post(
            "/conversations",
            json=valid_conversation_data
        )
        assert response.status_code == 200
        
        # Verify the conversation is in the database with normalized link
        conversation_id = UUID(response.json()["id"])
        conversation_in_db = db.query(Conversation).filter_by(id=conversation_id).first()
        assert conversation_in_db.user_friendly_link == "test-convo-link"


    def test_create_conversation_no_link(self, authenticated_clients, valid_conversation_data):
        """
        Test the successful creation of a conversation if the optional user-friendly link is not provided
        Expected Behavior:
        - The API returns a 200 status code
        """
        authenticated_client = authenticated_clients(1)["user1"]
        valid_conversation_data.pop("user_friendly_link")
        
        response = authenticated_client.post(
            "/conversations",
            json=valid_conversation_data
        )
        assert response.status_code == 200


    def test_cannot_create_conversation_with_existing_friendly_link(
        self, 
        authenticated_clients, 
        valid_conversation_data
    ):
        """
        Test handling of duplicate user-friendly link creation attempts from the same user
        Expected Behavior:
        - The API returns a 409 status code
        - The response JSON contains an "detail" field with the description "User friendly link already exists"
        """
        friendly_link = "existing-link"
        authenticated_client = authenticated_clients(1)["user1"]

        response1 = authenticated_client.post(
            "/conversations",
            json={**valid_conversation_data, "user_friendly_link": friendly_link}
        )
        assert response1.status_code == 200

        response2 = authenticated_client.post(
            "/conversations",
            json={**valid_conversation_data, "user_friendly_link": friendly_link}
        )
        assert response2.status_code == 409
        assert response2.json() == {"detail": "User friendly link already exists"}


class TestReadConversations:
    def test_read_conversations_returns_empty_list(self, authenticated_clients, unique_token):
        """
        Test that an empty list is returned when a user has not created a conversation
        Expected Behavior:
        - The API returns a 200 status code
        - The response JSON contains an empty list
        """
        authenticated_client = authenticated_clients(1)["user1"]
        
        response = authenticated_client.get("/conversations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


    def test_read_conversations_returns_a_list(self, authenticated_clients, create_conversation):
        """
        Test a list of conversations created by the user is returned
        Expected Behavior:
        - The API returns a 200 status code
        - The response JSON contains a list of the user-created conversations
        """
        authenticated_client = authenticated_clients(1)["user1"]
        
        conversation_response = create_conversation(authenticated_client)
        assert conversation_response.status_code == 200

        response = authenticated_client.get(
            "/conversations",
        )
        assert response.status_code == 200

        conversations = response.json()
        assert isinstance(conversations, list)
        assert len(conversations) >= 1
    

    def test_read_conversations_unauthenticated(self, client):
        """
        Test handling of an unauthenticated client attempting to retrieve their conversations
        Expected Behavior:
        - The API returns a 422 status code
        """
        client.cookies.clear()
        response = client.get("/conversations")
        assert response.status_code == 422
    

    def test_read_conversations_with_invalid_token(self, client):
        """
        Test handling of a client with an invalid token accessing the endpoint
        Expected Behavior:
        - The API returns a 401 status code
        - The response JSON contains an "detail" field with the description "Invalid token"
        """
        client.cookies.set("access_token", "fake.token.here")
        
        response = client.get("/conversations")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"


    def test_read_conversations_schema(
        self, 
        authenticated_clients, 
        create_conversation
    ):
        """
        Test the conversation object in the returned list contains exactly the expected fields
        """
        authenticated_client = authenticated_clients(1)["user1"]

        create_conversation(authenticated_client, {"name": "Schema Test Conversation"})
        create_conversation(authenticated_client, {"name": "Schema Test Conversation 2"})

        response = authenticated_client.get("/conversations")
        assert response.status_code == 200
        
        conversations = response.json()
        assert isinstance(conversations, list)
        assert len(conversations) >= 1

        for retrieved_conversation in conversations:
            try:
                validated_conversation = ConversationResponse(**retrieved_conversation)
                assert isinstance(validated_conversation, ConversationResponse)
            except Exception as e:
                pytest.fail(f"Returned conversation failed schema validation: {e}")


class TestReadConversation:
    def test_can_read_conversation_created_by_current_user(
        self,
        authenticated_client,
        create_conversation
    ):
        """
        Test a user is able to retrieve the details of a conversation they have created
        Expected Behavior:
        - The API returns a 200 status code
        """
        conversation_id = create_conversation(authenticated_client).json()["id"]

        response = authenticated_client.get(
            f"/conversations/{UUID(conversation_id)}",
        )
        assert response.status_code == 200
    

    def test_can_read_another_users_conversation(
        self,
        authenticated_clients,
        create_conversation,
    ):
        """
        Test a user is able to retrieve the details of another user's conversation
        Expected Behavior:
        - The API returns a 200 status code
        """
        clients = authenticated_clients(2)
        user1_client = clients["user1"]
        user2_client = clients["user2"]

        # User 1 creates a conversation
        conversation_id = create_conversation(user1_client).json()["id"]

        # User 2 tries to read User 1's conversation
        response = user2_client.get(
            f"/conversations/{UUID(conversation_id)}",
        )
        assert response.status_code == 200


    def test_read_conversation_unauthenticated(self, client, create_conversation):
        """
        Test handling of an unauthenticated client attempting to read a specified conversation
        Expected Behavior:
        - The API returns a 422 status code
        """
        conversation_id = create_conversation().json()["id"]

        client.cookies.clear()
        response = client.get(f"/conversations/{UUID(conversation_id)}")
        assert response.status_code == 422


    def test_read_conversation_not_found(self, authenticated_client):
        """
        Test handling of a user attempting to retrive the details of a non-existent conversation
        Expected Behavior:
        - The API returns a 404 status code 
        """
        response = authenticated_client.get(
            f"/conversations/{uuid4()}"
        )
        assert response.status_code == 404
    

    def test_read_conversations_with_invalid_token(self, client, create_conversation):
        """
        Test a client with an invalid token attempting to read a specified conversation
        Expected Behavior:
        - The API returns a 401 status code
        - The response JSON contains an "detail" field with the description "Invalid token"
        """
        conversation_id = create_conversation().json()["id"]
        
        # a client with an invalid token attempts to read the conversation
        client.cookies.set("access_token", "fake.token.here")   
        response = client.get(f"/conversations/{conversation_id}")

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"


    def test_read_conversation_format(
        self, 
        authenticated_clients, 
        create_conversation
    ):
        """
        Test the returned conversation object contains exactly the expected fields
        """
        authenticated_client = authenticated_clients(1)["user1"]
        conversation_id = create_conversation(authenticated_client).json()["id"]

        response = authenticated_client.get(f"/conversations/{conversation_id}")
        assert response.status_code == 200
        
        retrieved_conversation = response.json()
        try:
            validated_conversation = ConversationResponse(**retrieved_conversation)
            assert isinstance(validated_conversation, ConversationResponse)
        except Exception as e:
            pytest.fail(f"Returned conversation failed schema validation: {e}")


class TestUpdateConversation:
    def test_can_update_own_conversation(self, authenticated_client, create_conversation):
        """
        Test a user can modify the settings of a conversation they created
        Expected Behavior:
        - The API returns a 200 status code
        - The response JSON contains an "id" field with the conversation's id
        """
        conversation_id = create_conversation(authenticated_client, {"display_unmoderated": True}).json()["id"]
        
        # Verify initial value for display_unmoderated
        get_response = authenticated_client.get(f"/conversations/{conversation_id}")
        assert get_response.status_code == 200
        assert get_response.json()["display_unmoderated"] is True
        
        response = authenticated_client.put(
            f"/conversations/{conversation_id}",
            json={"display_unmoderated": "false"},
        ) 
        assert response.status_code == 200
        assert response.json() == {"id": conversation_id}

        # Verify the update
        get_response = authenticated_client.get(f"/conversations/{conversation_id}")
        assert get_response.status_code == 200
        assert get_response.json()["display_unmoderated"] is False
    

    def test_cannot_update_anothers_conversation(self, create_conversation, authenticated_clients):
        """
        Test a user cannot update the settings of another user's conversation
        Expected Behavior:
        - The API returns a 403 status code
        """
        clients = authenticated_clients(2) 
        conversation_owner = clients["user1"]
        another_user = clients["user2"]
        
        conversation_id = create_conversation(conversation_owner, {"display_unmoderated": True}).json()["id"]

        response = another_user.put(
            f"/conversations/{conversation_id}",
            json={"display_unmoderated": False}
        )
        assert response.status_code == 403
    
    
    def test_update_conversation_not_found(self, authenticated_client):
        """
        Test the handling of a user attempting to update the settings of a conversation that does not exist
        Expected Behavior:
        - The API returns a 404 status code 
        """
        response = authenticated_client.put(
            f"/conversations/{uuid4()}",
            json={"display_unmoderated": "false"},
        )
        assert response.status_code == 404


    def test_invalid_token(self, client, create_conversation):
        """
        Test the handling of a client with an invalid token attempting to update another user's conversation setting
        Expected Behavior:
        - The API returns a 401 status code
        """
        conversation_id = create_conversation().json()["id"]        
        
        client.cookies.set("access_token", "invalid_token")
        response = client.put(
            f"/conversations/{conversation_id}",
            json={"display_unmoderated": "false"}
        )
        assert response.status_code == 401
    

    def test_missing_token(self, client, create_conversation):
        """
        Test the handling of an unauthenticated user attempting to change the setting of another user's conversation setting
        Expected Behavior:
        - The API returns a 422 status code
        """
        conversation_id = create_conversation().json()["id"]
        
        # an unauthenticated client attempts to update the conversation
        client.cookies.clear()
        response = client.put(
            f"/conversations/{conversation_id}",
            json={"display_unmoderated": "false"}
        )
        
        assert response.status_code == 422  # should we get this to be 401 instead?
    

    def test_invalid_data(self, authenticated_client, create_conversation):
        """
        Test the handling of a user attempting to update the settings of their conversation with invalid data type
        Expected Behavior:
        - The API returns a 422 status code
        """
        conversation_id = create_conversation(authenticated_client).json()["id"]
        
        response = authenticated_client.put(
            f"/conversations/{conversation_id}",
            json={"display_unmoderated": "hello"}
        )
        assert response.status_code == 422


    def test_empty_update(self, authenticated_client, create_conversation):
        """
        Test the handling of a user updating their conversation without sending any data
        Expected Behavior:
        - The API returns a 200 status code
        """
        conversation_id = create_conversation(authenticated_client).json()["id"]
        
        response = authenticated_client.put(
            f"/conversations/{conversation_id}",
            json={}
        )
        
        assert response.status_code == 200


class TestDeleteConversation:
    def test_can_delete_own_conversation(self, authenticated_client, create_conversation):
        """
        Test the successful deletion of a conversation by the user that created the conversation
        Expected Behavior:
        - The API returns a 200 status code
        - The response JSON contains an "detail" field with the description "Conversation deleted successfully" and the conversation's id
        """
        conversation_id = create_conversation(authenticated_client).json()["id"]
        
        response = authenticated_client.delete(f"/conversations/{conversation_id}") 
        assert response.status_code == 200
        assert response.json() == {"detail": "Conversation deleted successfully", "id": conversation_id}

        # double check the conversation is actually deleted
        get_response = authenticated_client.get(f"/conversations/{conversation_id}")
        assert get_response.status_code == 404
    

    def test_cannot_delete_anothers_conversation(self, create_conversation, authenticated_clients):
        """
        Test the handling of a user attempting to delete another user's conversation
        Expected Behavior:
        - The API returns a 403 status code
        - The response JSON contains an "detail" field with the description "Not authorized"
        """
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]

        conversation_id = create_conversation(conversation_owner).json()["id"]

        response = another_user.delete(f"/conversations/{conversation_id}")
        assert response.status_code == 403
        assert response.json() == {"detail": "Not authorized"}
    

    def test_delete_conversation_not_found(self, authenticated_client):
        """
        Test handling of a user attempting to delete a non-existent conversation
        Expected Behavior:
        - The API returns a 404 status code
        """
        response = authenticated_client.delete(
            f"/conversations/{uuid4()}"
        )
        assert response.status_code == 404
    

    def test_delete_conversation_invalid_token(self, client, authenticated_client, create_conversation):
        """
        Test handling of a client with an invalid token attempting to delete a user's conversation
        Expected Behavior:
        - The API returns a 401 status code
        """
        conversation_id = create_conversation(authenticated_client).json()["id"]
        
        client.cookies.set("access_token", "invalid_token")
        response = client.delete(f"/conversations/{conversation_id}")
        assert response.status_code == 401


class TestGetConversationIdByFriendlyLink:
    def test_can_get_conversation_id_of_own_conversation(self, authenticated_client, create_conversation):
        friendly_link = "link-to-conversation"
        conversation_id = create_conversation(authenticated_client, {"user_friendly_link": friendly_link}).json()["id"]
        
        response = authenticated_client.get(
            f"/conversations/friendly-link/{friendly_link}/id"
        )    
        assert response.status_code == 200
        assert response.json() == conversation_id


    def test_can_get_conversation_id_of_anothers_conversation(self, authenticated_clients, create_conversation):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]
        
        friendly_link = "this-link-to-conversation"
        conversation_id = create_conversation(conversation_owner, {"user_friendly_link": friendly_link}).json()["id"]
        
        response = another_user.get(
            f"/conversations/friendly-link/{friendly_link}/id"
        )    
        assert response.status_code == 200
        assert response.json() == conversation_id


    def test_cannot_get_conversation_id_unauthenticated(self, client, authenticated_client, create_conversation):
        conversation_owner = authenticated_client
        
        # a conversation is created with a friendly link
        friendly_link = "a-link-to-conversation"
        conversation_response = create_conversation(conversation_owner, {"user_friendly_link": friendly_link}).json()
        
        # an unauthenticated client attempts to get the conversation ID using the friendly link
        client.cookies.clear()
        response = client.get(
            f"/conversations/friendly-link/{friendly_link}/id"
        )    
        assert response.status_code == 422
    

    def test_get_conversation_id_invalid_token(self, client, authenticated_client, create_conversation):
        conversation_owner = authenticated_client
        
        # a conversation is created with a friendly link
        friendly_link = "just-a-link-to-conversation"
        create_conversation(conversation_owner, {"user_friendly_link": friendly_link}).json()
        
        client.cookies.set("access_token", "invalid_token")
        response = client.get(f"/conversations/friendly-link/{friendly_link}/id")    
        assert response.status_code == 401
    
    
    def test_get_conversation_id_by_friendly_link_not_found(self, authenticated_client):
        response = authenticated_client.get(f"/conversations/friendly-link/nonexistent-link/id")
        assert response.status_code == 404


class TestCreateComment:
    def test_conversation_owner_can_create_comment(self, db, authenticated_client, create_conversation):
        conversation_id = create_conversation(authenticated_client).json()["id"]
        comment_data = {
            "content": "This is a test comment."
        }
        
        response = authenticated_client.post(
            f"/conversations/{conversation_id}/comments",
            json=comment_data
        )
        assert response.status_code == 200
        assert "id" in response.json()
        
        # Verify the comment is in the database
        comment_id = UUID(response.json()["id"])
        comment_in_db = db.query(Comment).filter_by(id=comment_id).first()
        assert comment_in_db is not None
        assert comment_in_db.content == comment_data["content"]


    def test_non_owner_can_create_comment_on_conversation(self, db, create_conversation, authenticated_clients):
        clients = authenticated_clients(3)
        conversation_owner = clients["user1"]
        user2_client = clients["user2"]
        user3_client = clients["user3"]

        # User 1 creates a conversation
        conversation_id = create_conversation(conversation_owner).json()["id"]
        
        # User 2 and User 3 create a comment each on User 1's conversation
        comment_data_user2 = {"content": "Comment from user 2"}
        response_user2 = user2_client.post(
            f"/conversations/{conversation_id}/comments",
            json=comment_data_user2
        )
        assert response_user2.status_code == 200

        comment_data_user3 = {"content": "Comment from user 3"}
        response_user3 = user3_client.post(
            f"/conversations/{conversation_id}/comments",
            json=comment_data_user3
        )
        assert response_user3.status_code == 200

        # Query the database to check both comments were created
        comments = db.query(Comment).filter_by(conversation_id=UUID(conversation_id)).all()
        assert len(comments) == 2
    

    def test_cannot_create_comment_when_missing_fields(self, authenticated_clients, create_conversation):
        authenticated_client = authenticated_clients(1)["user1"]
        
        conversation_id = create_conversation(authenticated_client).json()["id"]
        invalid_data = {}

        response = authenticated_client.post(
            f"/conversations/{conversation_id}/comments",
            json=invalid_data
        )
        assert response.status_code == 422
    

    def test_create_commment_conversation_not_found(self, authenticated_client):
        invalid_conversation_id = uuid4()
        comment_data = {
            "content": "This is a test comment."
        }

        response = authenticated_client.post(
            f"/conversations/{invalid_conversation_id}/comments",
            json=comment_data
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Conversation not found"}
    

    def test_create_comment_no_token(self, client, create_conversation):
        conversation_id = create_conversation().json()["id"]
        
        # an unathenticated client attempts to create a comment
        client.cookies.clear()
        response = client.post(
            f"/conversations/{conversation_id}/comments", json={"content": "Test comment"}
        )

        assert response.status_code == 422  # should we get this to be 401 instead?
    

    def test_create_comment_with_invalid_token(self, client, create_conversation):
        conversation_id = create_conversation().json()["id"]

        # a client with an invalid token attempts to create a comment
        client.cookies.set("access_token", "invalid_token")
        response = client.post(
            f"/conversations/{conversation_id}/comments", json={"content": "Test comment"}
        )
        assert response.status_code == 401


    def test_create_comment_invalid_conversation_id_type(self, authenticated_client):
        invalid_conversation_id = "not-a-uuid"

        response = authenticated_client.post(
            f"/conversations/{invalid_conversation_id}/comments", json={"content": "Test comment"}
        )

        assert response.status_code == 422
    

class TestReadComments:
    def test_conversation_owner_can_read_all_comments(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment
    ):
        clients = authenticated_clients(3)       
        conversation_owner = clients["user1"]
        user_2 = clients["user2"]
        user_3 = clients["user3"]
        
        conversation_id = create_conversation(conversation_owner).json()["id"]

        # Conversation owner and 2 other users create a comment each on the conversation
        conversation_owner_comment = "Owner's comment"
        user_2_comment = "User2's comment"
        user_3_comment = "User3's comment"
        create_comment(conversation_owner, conversation_id, conversation_owner_comment)
        create_comment(user_2, conversation_id, user_2_comment)
        create_comment(user_3, conversation_id, user_3_comment)

        response = conversation_owner.get(
            f"/conversations/{conversation_id}/comments"
        )
        
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) == 3

    
    def test_read_comments_as_different_user(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment
    ):
        clients = authenticated_clients(3)       
        conversation_owner = clients["user1"]
        user_2 = clients["user2"]
        user_3 = clients["user3"]

        conversation_id = create_conversation(conversation_owner).json()["id"]

        # Conversation owner and user 2 create a comment each on the conversation
        create_comment(conversation_owner, conversation_id, "Owner's comment")
        create_comment(user_2, conversation_id, "User2's comment")
        
        # User 3 reads the comments
        response = user_3.get(
            f"/conversations/{conversation_id}/comments"
        )
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) == 2
    

    def test_read_comments_format(self, authenticated_client, create_conversation, create_comment):
        conversation_owner = authenticated_client
        conversation_id = create_conversation(conversation_owner).json()["id"]

        # Create multiple comments by conversation owner
        count = 0
        while count < 5:
            create_comment(conversation_owner, conversation_id, f"Comment {count}")
            count += 1
        
        # Simulate a GET request without `include_user_info`
        response = conversation_owner.get(f"/conversations/{conversation_id}/comments")
        
        assert response.status_code == 200
        comments = response.json()
        assert all("id" in comment for comment in comments)
        assert all("content" in comment for comment in comments)
        assert all("vote" not in comment for comment in comments)


    def test_read_comments_format_with_user_info(
        self, 
        authenticated_client, 
        create_conversation, 
        create_comment
    ):
        conversation_owner = authenticated_client
        conversation_id = create_conversation(conversation_owner).json()["id"]
        
        comment_content = "This is a test comment."
        create_comment(conversation_owner, conversation_id, comment_content)

        response = authenticated_client.get(
            f"/conversations/{conversation_id}/comments?include_user_info=true"
        )
        assert response.status_code == 200
        
        comments = response.json()
        assert len(comments) == 1
        assert comments[0]["content"] == comment_content
        assert "vote" in comments[0]
    

    def test_invalid_include_user_info(self, authenticated_client, create_conversation):
        conversation_id = create_conversation(authenticated_client).json()["id"]
        
        # invalid query parameter for `include_user_info`
        response = authenticated_client.get(f"/conversations/{conversation_id}/comments?include_user_info=invalid_value")
        assert response.status_code == 422


    def test_read_comments_when_empty(self, authenticated_client, create_conversation):
        conversation_owner = authenticated_client
        conversation_id = create_conversation(conversation_owner).json()["id"]
        
        response = conversation_owner.get(f"/conversations/{conversation_id}/comments")
        assert response.status_code == 200

        # returns an empty list when no commments exist
        comments = response.json()
        assert isinstance(comments, list)
        assert len(comments) == 0


    def test_read_comments_with_invalid_token(self, client, create_conversation):
        conversation_id = create_conversation().json()["id"]
        
        client.cookies.set("access_token", "invalid_token")
        response = client.get(f"/conversations/{conversation_id}/comments")
        assert response.status_code == 401
    

    def test_read_comments_conversation_not_found(self, authenticated_client):
        non_existent_conversation_id = uuid4()

        response = authenticated_client.get(f"/conversations/{non_existent_conversation_id}/comments")
        assert response.status_code == 404
    

    def test_read_comments_no_token(self, client, create_conversation):
        conversation_id = create_conversation().json()["id"]
        
        client.cookies.clear()
        response = client.get(f"/conversations/{conversation_id}/comments")
        assert response.status_code == 422
    

    def test_read_only_approved_comments_when_display_unmoderated_is_false(
        self,
        authenticated_clients, 
        create_conversation, 
        create_comment,
        approve_comment
    ):
        clients = authenticated_clients(2)               
        conversation_owner = clients["user1"]
        user_2 = clients["user2"]

        # conversation owner creates a conversation that requires comments to be approved
        conversation_id = create_conversation(conversation_owner, {"display_unmoderated": False}).json()["id"]
        
        # user 2 creates two comments, one to be approved and one to be left unapproved
        not_approved_comment = "I am a silly cat."
        create_comment(user_2, conversation_id, not_approved_comment)
        approved_comment = "This comment will be approved."
        approved_comment_id = create_comment(user_2, conversation_id, approved_comment).json()["id"]
        
        # conversation owner approves one of the comments
        approve_response = approve_comment(conversation_owner, approved_comment_id)
        assert approve_response.status_code == 200

        # only the approved comment is returned when conversation owner queries
        response = conversation_owner.get(
            f"/conversations/{conversation_id}/comments"
        )
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) == 1
        assert comments[0]["content"] == approved_comment
        
        # only the approved comment is returned when another user queries
        response = user_2.get(
            f"/conversations/{conversation_id}/comments"
        )
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) == 1
        assert comments[0]["content"] == approved_comment


class TestVoteOnComment:
    def test_can_vote_on_another_users_comment_first_time(
        self, 
        authenticated_clients,
        create_conversation, 
        create_comment
    ):
        users = authenticated_clients(3)
        conversation_owner = users["user1"]
        user_2 = users["user2"]
        user_3 = users["user3"]

        conversation_id = create_conversation(conversation_owner).json()["id"]
        
        # conversation owner and user 2 create a comment each on the conversation
        owner_comment_id = create_comment(conversation_owner, conversation_id).json()["id"]
        user2_comment_id = create_comment(user_2, conversation_id).json()["id"]

        # user 3 votes on user 2's comment
        response = user_3.post(
            f"/comments/{user2_comment_id}/vote",
            json={"value": 1}
        )
        assert response.status_code == 200
        assert "id" in response.json()
        
        # user 3 votes on conversation owner's comment
        response = user_3.post(
            f"/comments/{owner_comment_id}/vote",
            json={"value": 1}
        )
        assert response.status_code == 200
        assert "id" in response.json()
        
        # user 2 votes on conversation owner's comment
        response = user_2.post(
            f"/comments/{owner_comment_id}/vote",
            json={"value": 1}
        )
        assert response.status_code == 200
        assert "id" in response.json()
        
        # conversation owner votes on user2's comment
        response = conversation_owner.post(
            f"/comments/{user2_comment_id}/vote",
            json={"value": 1}
        )
        assert response.status_code == 200
        assert "id" in response.json()
    

    def test_can_update_vote_on_another_users_comment(
        self, 
        authenticated_clients,
        create_conversation, 
        create_comment
    ):
        users = authenticated_clients(3)
        conversation_owner = users["user1"]
        user_2 = users["user2"]
        user_3 = users["user3"]

        conversation_id = create_conversation(conversation_owner).json()["id"]
        comment_id = create_comment(user_2, conversation_id).json()["id"]

        # user 3 votes on user 2's comment for the first time
        response = user_3.post(
            f"/comments/{comment_id}/vote",
            json={"value": 1}
        )
        assert response.status_code == 200
        vote_id = response.json().get("id")

        # user 3 votes again on user 2's comment
        response = user_3.post(
            f"/comments/{comment_id}/vote",
            json={"value": -1}
        )
        assert response.status_code == 200

        # check that vote id is the same for both interactions
        assert response.json().get("id") == vote_id
    

    def test_can_vote_on_own_comment(self, authenticated_clients, create_conversation, create_comment):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        user_2 = clients["user2"]
        
        conversation_id = create_conversation(conversation_owner).json()["id"]
        
        owner_comment_id = create_comment(conversation_owner, conversation_id).json()["id"]
        user2_comment_id = create_comment(user_2, conversation_id).json()["id"]

        # conversation owner votes on their own comment
        response = conversation_owner.post(
            f"/comments/{owner_comment_id}/vote",
            json={"value": 1}
        )
        assert response.status_code == 200
        assert "id" in response.json()

        # user 2 votes on their own comment
        response = user_2.post(
            f"/comments/{user2_comment_id}/vote",
            json={"value": 1}
        )
        assert response.status_code == 200
        assert "id" in response.json()
    

    def test_vote_on_comment_not_found(self, authenticated_client):
        non_existent_comment_id = uuid4()
        
        response = authenticated_client.post(
            f"/comments/{non_existent_comment_id}/vote",
            json={"value": 1}
        )
        
        assert response.status_code == 404
        assert response.json() == {"detail": "Comment not found"}
    

    def test_vote_on_comment_unauthenticated(self, create_conversation, create_comment, authenticated_client):
        client = authenticated_client

        conversation_id = create_conversation(client).json()["id"]
        comment_id = create_comment(client, conversation_id).json()["id"]

        client.cookies.clear()
        response = client.post(
            f"/comments/{comment_id}/vote",
            json={"value": 1}
        )

        assert response.status_code == 422  # should we get this to be 401 instead?
    

    def test_vote_on_comment_with_invalid_token(self, client, create_conversation, create_comment):
        conversation_id = create_conversation().json()["id"]
        comment_id = create_comment(client, conversation_id).json()["id"]

        client.cookies.set("access_token", "invalid_token")
        response = client.post(
            f"/comments/{comment_id}/vote",
            json={"value": 1}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"
    

    def test_vote_on_comment_invalid_data(self, authenticated_client, create_conversation, create_comment):
        conversation_id = create_conversation(authenticated_client).json()["id"]
        comment_id = create_comment(authenticated_client, conversation_id).json()["id"]

        response = authenticated_client.post(
            f"/comments/{comment_id}/vote",
            json={"value": "invalid_value"}
        )
        
        assert response.status_code == 422


    def test_multiple_users_can_vote_independently_on_same_comment(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment
    ):
        users = authenticated_clients(3)
        conversation_owner = users["user1"]
        user_2 = users["user2"]
        user_3 = users["user3"]

        # conversation owner creates a comment on their conversation
        conversation_id = create_conversation(conversation_owner).json()["id"]
        comment_id = create_comment(conversation_owner, conversation_id).json()["id"]

        # User 2 votes on the comment
        user_2_vote_response = user_2.post(
            f"/comments/{comment_id}/vote",
            json={"value": 1}
        )
        assert user_2_vote_response.status_code == 200

        # User 3 votes on the comment
        user_3_vote_response = user_3.post(
            f"/comments/{comment_id}/vote",
            json={"value": -1}
        )
        assert user_3_vote_response.status_code == 200

        # ensure that the vote IDs are different
        assert user_2_vote_response.json()["id"] != user_3_vote_response.json()["id"]


class TestGetNextRemainingComment:
    def test_get_next_remaining_comment_success(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment, 
        approve_comment
    ):
        clients = authenticated_clients(3)
        conversation_owner = clients["user1"]
        user_2 = clients["user2"]
        user_3 = clients["user3"]

        conversation_id = create_conversation(conversation_owner).json()["id"]
        
        # a comment is created and approved for the new conversation
        comment_id = create_comment(user_3, conversation_id, "Comment made by someone out there").json()["id"]
        approve_response = approve_comment(conversation_owner, comment_id)
        assert approve_response.status_code == 200

        # conversation owner can fetch the next remaining comment
        response = conversation_owner.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 200

        # user 2 can also fetch the next remaining comment
        response = user_2.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 200


    def test_get_next_remaining_comment_format(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment, 
        approve_comment
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        user_2 = clients["user2"]

        conversation_id = create_conversation(conversation_owner).json()["id"]
        
        comment_id = create_comment(conversation_owner, conversation_id, "Comment").json()["id"]
        approve_response = approve_comment(conversation_owner, comment_id)

        response = user_2.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 200

        RemainingCommentResponse(**response.json())
    

    def test_get_next_remaining_comment_no_comments(self, authenticated_client, create_conversation):
        conversation_id = create_conversation(authenticated_client).json()["id"]
        
        response = authenticated_client.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "No remaining comments found"}
    

    def test_get_next_remaining_comment_skips_own_comments(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment, 
        approve_comment
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        user_2 = clients["user2"]

        conversation_id = create_conversation(conversation_owner).json()["id"]

        # user 2 creates a comment that is approved by the conversation owner
        user1_comment_id = create_comment(user_2, conversation_id, "User 2's comment").json()["id"]
        approve_comment(conversation_owner, user1_comment_id)

        # conversation owner fetches the next remaining comment, should see user 1's comment
        response = conversation_owner.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 200

        # user 2 should see no remaining comments since the only comment is their own
        response = user_2.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "No remaining comments found"}
    

    def test_get_next_remaining_comment_skips_voted_comments(
        self,
        authenticated_clients,
        create_conversation,
        create_comment,
        approve_comment,
        vote_on_comment,
    ):
        clients = authenticated_clients(3)
        conversation_owner = clients["user1"]
        user_2 = clients["user2"]
        user_3 = clients["user3"]

        conversation_id = create_conversation(conversation_owner).json()["id"]

        # user 2 creates two comments
        comment_1_id = create_comment(user_2, conversation_id, "A comment").json()["id"]
        comment_2_id = create_comment(user_2, conversation_id, "Another comment that is definitely different from the first").json()["id"]

        # both comments approved by conversation owner
        approve_response = approve_comment(conversation_owner, comment_1_id)
        approve_response = approve_comment(conversation_owner, comment_2_id)

        # user 3 fetches the next remaining comment
        response = user_3.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 200
        first_remaining_comment_returned = response.json()["comment"]
        
        # user 3 votes on one of the comments
        vote_response = vote_on_comment(user_3, first_remaining_comment_returned["id"], 1)
        assert vote_response.status_code == 200

        # user 3 fetches the next remaining comment again, should get the other comment
        response = user_3.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 200
        second_remaining_comment_returned = response.json()["comment"]
        assert first_remaining_comment_returned["id"] != second_remaining_comment_returned["id"]

        # User 3 votes on the second comment
        vote_response = vote_on_comment(user_3, second_remaining_comment_returned["id"], -1)
        assert vote_response.status_code == 200
        
        # now User 3 should have no remaining comments
        response = user_3.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "No remaining comments found"}


    def test_get_next_remaining_comment_skips_rejected_comments(
        self,
        authenticated_clients,
        create_conversation,
        create_comment,
        approve_comment,
        reject_comment,
        vote_on_comment
    ):
        clients = authenticated_clients(3)
        conversation_owner = clients["user1"]
        user_2 = clients["user2"]
        user_3 = clients["user3"]

        conversation_id = create_conversation(conversation_owner).json()["id"]

        # user 2 creates two comments
        approved_comment_id = create_comment(user_2, conversation_id, "I will be approved.").json()["id"]
        rejected_comment_id = create_comment(user_2, conversation_id, "I am a silly cat.").json()["id"]

        # conversation owner approves one comment and rejects the other
        approve_response = approve_comment(conversation_owner, approved_comment_id)
        reject_response = reject_comment(conversation_owner, rejected_comment_id)

        # user 3 tries to get the next remaining comment, should only see the approved one
        response = user_3.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 200
        remaining_comment = response.json()["comment"]
        assert remaining_comment["id"] == approved_comment_id

        # user 3 votes on the approved comment
        vote_on_comment(user_3, remaining_comment["id"], 1)

        # user 3 tries to get the next remaining comment again, should now see no comments
        response = user_3.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "No remaining comments found"}


    def test_get_next_remaining_comment_conversation_not_found(self, authenticated_client):
        non_existent_conversation_id = uuid4()
        
        response = authenticated_client.get(
            f"/conversations/{non_existent_conversation_id}/comments/remaining"
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Conversation not found"}
    

    def test_get_next_remaining_comment_unauthenticated(self, client, create_conversation):
        conversation_id = create_conversation().json()["id"]
        
        client.cookies.clear()
        response = client.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        
        assert response.status_code == 422  # should we get this to be 401 instead?
    

    def test_get_next_remaining_comment_with_invalid_token(self, client, create_conversation):
        conversation_id = create_conversation().json()["id"]
        
        client.cookies.set("access_token", "invalid_token")
        response = client.get(
            f"/conversations/{conversation_id}/comments/remaining"
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"
