from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from convergent import models
from convergent.auth.user import CurrentUser
from convergent.database import Database
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/moderation")


class Comment(BaseModel):
    id: UUID
    content: str
    user_id: UUID
    approved: Optional[bool] = None


@router.get("/conversations/{conversation_id}/comments", response_model=list[Comment])
async def read_comments(
    conversation_id: UUID, db: Database, current_user: CurrentUser
):
    conversation: models.Conversation | None = db.query(models.Conversation).get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.author != current_user:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation.comments


@router.put("/comments/{comment_id}/approve")
async def approve_comment(comment_id: UUID, db: Database, current_user: CurrentUser):
    comment_db = db.query(models.Comment).get(comment_id)
    if comment_db is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment_db.conversation.author != current_user:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment_db.approved = True
    db.commit()
    return {"success": True}
