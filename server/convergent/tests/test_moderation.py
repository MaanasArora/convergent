from pydantic import BaseModel, ConfigDict
from uuid import UUID, uuid4
from typing import Optional
from convergent.models import Conversation
import pytest
from datetime import datetime



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
    content: str
    user_id: UUID
    approved: Optional[bool] = None

    model_config = ConfigDict(extra='forbid')



class TestReadConversations:
    def test_returns_empty_list_when_no_conversations(
        self, 
        authenticated_client
    ):
        response = authenticated_client.get("/moderation/conversations")
        assert response.status_code == 200
        
        conversations = response.json()
        assert isinstance(conversations, list)
        assert len(conversations) == 0
    
    
    def test_read_only_conversations_of_current_user(
        self, 
        authenticated_clients, 
        create_conversation, 
    ):
        clients = authenticated_clients(2)
        user_1 = clients["user1"]
        user_2 = clients["user2"]

        # create 1 conversations for user 1
        create_conversation(user_1, {"name": "User1's Conversation"})

        # create 3 converasations for user 2
        for i in range(3):
            create_conversation(user_2, {"name": f"User2's Conversation {i+1}"})

        # fetch conversations for user 1
        response = user_1.get("/moderation/conversations")
        assert response.status_code == 200
        
        # ensure only 1 conversation is returned and it belongs to user 1
        conversations = response.json()
        assert isinstance(conversations, list)
        assert len(conversations) == 1
        assert conversations[0]['author']['username'] == "user1"
        
        # fetch conversations for user 2
        response = user_2.get("/moderation/conversations")
        assert response.status_code == 200
        
        # ensure 3 conversations are returned and it belongs to user 2
        conversations = response.json()
        assert isinstance(conversations, list)
        assert len(conversations) == 3
        for conv in conversations:
            assert conv['author']['username'] == "user2"
    

    def test_unauthenticated_access(self, client, create_conversation):
        # create a conversation to ensure there is data in the database
        create_conversation()
        
        client.cookies.clear()
        response = client.get("/moderation/conversations")
        assert response.status_code == 422  # should be 401 but FastAPI returns 422 for missing cookie
    

    def test_read_conversation_schema(
        self, 
        authenticated_client, 
        create_conversation
    ):
        conversation_id = create_conversation(authenticated_client).json()["id"]

        response = authenticated_client.get("/moderation/conversations")
        assert response.status_code == 200
        
        # ensure the response matches the ConversationResponse schema
        retrieved_conversation = response.json()[0]
        ConversationResponse(**retrieved_conversation)


class TestReadComments:
    def test_returns_empty_list_when_no_comments(
        self, 
        authenticated_client, 
        create_conversation
    ):
        # create a conversation with no comments
        conversation_id = create_conversation(authenticated_client).json()["id"]

        # fetch comments for the conversation
        response = authenticated_client.get(f"/moderation/conversations/{conversation_id}/comments")
        assert response.status_code == 200
        
        # ensure an empty list is returned
        comments = response.json()
        assert isinstance(comments, list)
        assert len(comments) == 0


    def test_can_read_all_comments_of_own_conversation(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]

        # conversation owner creates a conversation
        conversation_id = create_conversation(conversation_owner).json()["id"]

        # another user adds comments to the conversation
        comment_contents = ["First comment", "Second comment", "Third comment"]
        for content in comment_contents:
            comment_response = create_comment(
                another_user, 
                conversation_id, 
                content
            )

        # conversation owner fetches comments for the conversation
        response = conversation_owner.get(f"/moderation/conversations/{conversation_id}/comments")
        assert response.status_code == 200
        
        # ensure all comments are returned
        comments = response.json()
        assert len(comments) == len(comment_contents)
        returned_contents = [comment["content"] for comment in comments]
        for content in comment_contents:
            assert content in returned_contents
    

    def test_cannot_read_comments_of_others_conversation(
        self, 
        authenticated_clients, 
        create_conversation
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]

        conversation_id = create_conversation(conversation_owner).json()["id"]

        # another user tries to fetch comments for the conversation
        response = another_user.get(f"/moderation/conversations/{conversation_id}/comments")
        assert response.status_code == 404


    def test_only_returns_comments_for_specified_conversation(
        self,
        authenticated_client,
        create_conversation,
        create_comment
    ):
        # create two conversations
        conversation1_id = create_conversation(authenticated_client).json()["id"]       
        conversation2_id = create_conversation(authenticated_client).json()["id"]

        # add comments to both conversations
        conversation1_comments = ["First comment", "Second comment", "Third comment"]
        for content in conversation1_comments:
            create_comment(
                authenticated_client, 
                conversation1_id, 
                content
            )
        conversation2_comments = ["Another comment", "Yet another comment"]
        for content in conversation2_comments:
            create_comment(
                authenticated_client, 
                conversation2_id, 
                content
            )
        
        # fetch comments for the conversation 1
        response = authenticated_client.get(f"/moderation/conversations/{conversation1_id}/comments")
        assert response.status_code == 200
        
        # ensure only comments for conversation 1 are returned
        comments = response.json()
        assert len(comments) == len(conversation1_comments)
        returned_contents = [comment["content"] for comment in comments]
        for content in conversation1_comments:
            assert content in returned_contents


    def test_unauthenticated_access(self, client, authenticated_client, create_conversation, create_comment):
        conversation_id = create_conversation(authenticated_client).json()["id"]

        create_comment(
            authenticated_client,
            conversation_id,
            "A comment to test unauthenticated access"
        )

        # unauthenticated client tries to fetch comments
        client.cookies.clear()
        response = client.get(f"/moderation/conversations/{conversation_id}/comments")
        assert response.status_code == 422


    def test_returns_404_for_nonexistent_conversation(
        self, 
        authenticated_client
    ):
        non_existent_id = uuid4()

        response = authenticated_client.get(f"/moderation/conversations/{non_existent_id}/comments")
        assert response.status_code == 404
        assert response.json()["detail"] == "Conversation not found"
    

    def test_comment_schema(
        self, 
        authenticated_client, 
        create_conversation, 
        create_comment
    ):
        conversation_id = create_conversation(authenticated_client).json()["id"]

        create_comment(authenticated_client, conversation_id, "Test comment content")

        response = authenticated_client.get(f"/moderation/conversations/{conversation_id}/comments")
        assert response.status_code == 200
        
        # ensure the response matches the CommentResponse schema
        retrieved_comment = response.json()[0]
        CommentResponse(**retrieved_comment)


class TestApproveComment:
    def test_can_approve_comment_on_own_conversation(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment, 
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]

        # conversation owner creates a conversation
        conversation_id = create_conversation(conversation_owner).json()["id"]

        # another user adds a comment to the conversation
        comment_id = create_comment(
            another_user, 
            conversation_id, 
            "Comment to be approved"
        ).json()["id"]

        # conversation owner approves the comment
        approve_response = conversation_owner.put(
            f"/moderation/comments/{comment_id}/approve"
        )
        assert approve_response.status_code == 200
        assert approve_response.json()["success"] is True

        # fetch comments to verify approval status
        response = conversation_owner.get(f"/moderation/conversations/{conversation_id}/comments")
        assert response.status_code == 200
        comments = response.json()
        
        # ensure the comment is marked as approved
        approved_comments = [c for c in comments if c["id"] == comment_id and c.get("approved") is True]
        assert len(approved_comments) == 1


    def test_cannot_approve_comment_in_others_conversation(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]

        # conversation owner creates a conversation
        conversation_id = create_conversation(conversation_owner).json()["id"]

        # another user adds a comment to the conversation
        comment_id = create_comment(
            another_user, 
            conversation_id, 
            "Comment that should not be approvable by another user"
        ).json()["id"]

        # another user tries to approve the comment
        approve_response = another_user.put(
            f"/moderation/comments/{comment_id}/approve"
        )
        assert approve_response.status_code == 404
        assert approve_response.json()["detail"] == "Comment not found"


    def test_handle_nonexistent_comment(
        self, 
        authenticated_client
    ):
        non_existent_comment_id = uuid4()
        
        approve_response = authenticated_client.put(
            f"/moderation/comments/{non_existent_comment_id}/approve"
        )
        assert approve_response.status_code == 404
        assert approve_response.json()["detail"] == "Comment not found"
    

    def test_handle_unauthenticated_user(
        self, 
        client, 
        authenticated_clients, 
        create_conversation, 
        create_comment
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]

        # conversation owner creates a conversation
        conversation_id = create_conversation(conversation_owner).json()["id"]
        
        # another user adds a comment to the conversation
        comment_id = create_comment(
            another_user, 
            conversation_id, 
            "Comment to test unauthenticated approval"
        ).json()["id"]

        # unauthenticated client tries to approve the comment
        client.cookies.clear()
        approve_response = client.put(
            f"/moderation/comments/{comment_id}/approve"
        )
        assert approve_response.status_code == 422


class TestRejectComment:
    def test_can_reject_comment_on_own_conversation(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment, 
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]

        # conversation owner creates a conversation
        conversation_id = create_conversation(conversation_owner).json()["id"]

        # another user adds a comment to the conversation
        comment_id = create_comment(
            another_user, 
            conversation_id, 
            "Comment to be rejected"
        ).json()["id"]

        # conversation owner rejects the comment
        reject_response = conversation_owner.put(
            f"/moderation/comments/{comment_id}/reject"
        )
        assert reject_response.status_code == 200
        assert reject_response.json()["success"] is True

        # fetch comments to verify rejection status
        response = conversation_owner.get(f"/moderation/conversations/{conversation_id}/comments")
        assert response.status_code == 200
        
        # ensure the comment is marked as rejected
        comments = response.json()
        rejected_comments = [c for c in comments if c["id"] == comment_id and c.get("approved") is False]
        assert len(rejected_comments) == 1


    def test_cannot_reject_comment_in_others_conversation(
        self, 
        authenticated_clients, 
        create_conversation, 
        create_comment
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]

        # conversation owner creates a conversation
        conversation_id = create_conversation(conversation_owner).json()["id"]

        # another user adds a comment to the conversation
        comment_id = create_comment(
            another_user, 
            conversation_id, 
            "Comment that should not be rejectable by another user"
        ).json()["id"]

        # another user tries to reject the comment
        reject_response = another_user.put(
            f"/moderation/comments/{comment_id}/reject"
        )
        assert reject_response.status_code == 404
        assert reject_response.json()["detail"] == "Comment not found"
    

    def test_handle_nonexistent_comment(
        self, 
        authenticated_client
    ):
        non_existent_comment_id = uuid4()

        reject_response = authenticated_client.put(
            f"/moderation/comments/{non_existent_comment_id}/reject"
        )
        assert reject_response.status_code == 404
        assert reject_response.json()["detail"] == "Comment not found"
    

    def test_handle_unauthenticated_user(
        self, 
        client, 
        authenticated_clients, 
        create_conversation, 
        create_comment
    ):
        clients = authenticated_clients(2)
        conversation_owner = clients["user1"]
        another_user = clients["user2"]

        # conversation owner creates a conversation
        conversation_id = create_conversation(conversation_owner).json()["id"]

        # another user adds a comment to the conversation
        comment_id = create_comment(
            another_user, 
            conversation_id, 
            "Comment to test unauthenticated rejection"
        ).json()["id"]

        # unauthenticated client tries to reject the comment
        client.cookies.clear()
        reject_response = client.put(
            f"/moderation/comments/{comment_id}/reject"
        )
        assert reject_response.status_code == 422
