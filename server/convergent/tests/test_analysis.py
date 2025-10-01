from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import pytest
from convergent.models import Conversation, Comment


class TestConversationAnalysis:
    @pytest.mark.parametrize("num_comments", [4, 5])
    @pytest.mark.parametrize("users_per_group", [3, 4])
    def test_get_conversation_analysis(
        self,
        authenticated_clients,
        create_conversation,
        create_comment,
        num_comments,
        users_per_group,
    ):
        num_users = users_per_group * 2  # Two groups
        clients = authenticated_clients(num_users + 1)  # +1 for conversation owner
        conversation_owner_client = clients["user1"]

        other_clients = [clients[f"user{i}"] for i in range(2, num_users + 2)]
        pos_clients = other_clients[: users_per_group]
        neg_clients = other_clients[users_per_group :]

        conversation = create_conversation(conversation_owner_client)
        conversation = conversation.json()
        conversation_id = conversation["id"]

        # Add comments to the conversation
        comment_ids = []
        for client in other_clients:
            comment = create_comment(client, conversation_id, "This is a test comment.")
            comment_ids.append(comment.json()["id"])

        # Positive group
        for client in pos_clients:
            for comment_id in comment_ids:
                client.post(f"/comments/{comment_id}/vote", json={"value": 1})

        # Negative group
        for client in neg_clients:
            for comment_id in comment_ids:
                client.post(f"/comments/{comment_id}/vote", json={"value": -1})

        # Fetch conversation analysis
        response = conversation_owner_client.get(
            f"/analysis/conversation/{conversation_id}"
        )
        assert response.status_code == 200

        analysis = response.json()
        print(analysis)
        assert analysis["conversation_id"] == conversation_id
        assert len(analysis["groups"]) == 2  # Expecting 2 distinct groups
        for group in analysis["groups"]:
            print(group)
            assert len(group["users"]) == num_users // 2
        assert len(analysis["comments"]) == len(comment_ids)
