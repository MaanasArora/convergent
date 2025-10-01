from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException
from sqlalchemy import false, true
import urllib
from convergent import models
from convergent.auth.user import CurrentUser
from convergent.database import Database
from pydantic import BaseModel


router = APIRouter()


class UserBasic(BaseModel):
    id: UUID
    username: str


class Conversation(BaseModel):
    id: UUID
    name: str
    description: str = None
    author: UserBasic
    num_participants: int = None
    display_unmoderated: bool
    date_created: datetime = None
    is_active: bool = True
    user_friendly_link: Optional[str] = None


class ConversationCreate(BaseModel):
    name: str
    description: str = None
    display_unmoderated: bool = False
    user_friendly_link: Optional[str] = None


class Comment(BaseModel):
    id: UUID
    content: str


class CommentCreate(BaseModel):
    content: str


class Vote(BaseModel):
    value: int


class CommentDetail(Comment):
    pass


class ConversationDetail(Conversation):
    pass


class CommentWithUserInfo(CommentDetail):
    vote: Optional[int] = None


class ConversationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    display_unmoderated: Optional[bool] = False


def get_conversation_details(
    conversation_db: models.Conversation, db: Database, current_user: CurrentUser
):
    num_participants = (
        db.query(models.Comment.user_id)
        .filter(models.Comment.conversation == conversation_db)
        .distinct()
        .count()
    )

    conversation = Conversation.model_validate(conversation_db, from_attributes=True)
    conversation.num_participants = num_participants

    return conversation


@router.get("/conversations", response_model=list[Conversation])
async def read_conversations(db: Database, current_user: CurrentUser):
    conversations = db.query(models.Conversation).all()

    return [
        get_conversation_details(conversation, db, current_user)
        for conversation in conversations
    ]


@router.get(
    "/conversations/friendly-link/{user_friendly_link}/id",
    response_model=UUID,
)
async def get_conversation_id_by_friendly_link(
    user_friendly_link: str, db: Database, current_user: CurrentUser
):
    conversation = (
        db.query(models.Conversation)
        .filter(
            models.Conversation.user_friendly_link == user_friendly_link,
            models.Conversation.is_active == true(),
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation.id


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def read_conversation(
    conversation_id: UUID, db: Database, current_user: CurrentUser
):
    conversation_db = db.query(models.Conversation).get(conversation_id)
    if conversation_db is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation = get_conversation_details(conversation_db, db, current_user)
    return conversation


def get_comment_user_info(
    comment: models.Comment, db: Database, current_user: CurrentUser
):
    vote = (
        db.query(models.Vote)
        .filter(models.Vote.comment == comment, models.Vote.user == current_user)
        .first()
    )
    return {
        "id": comment.id,
        "content": comment.content,
        "vote": vote.value if vote else None,
    }


@router.get(
    "/conversations/{conversation_id}/comments",
    response_model=list[CommentDetail] | list[CommentWithUserInfo],
)
async def read_comments(
    conversation_id: UUID,
    db: Database,
    current_user: CurrentUser,
    include_user_info: bool = False,
):
    conversation = db.query(models.Conversation).get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    comments = conversation.comments

    if not conversation.display_unmoderated:
        comments = list(filter(lambda c: c.approved, comments))

    if include_user_info:
        return [
            get_comment_user_info(comment, db, current_user) for comment in comments
        ]
    else:
        return comments


@router.post("/conversations")
async def create_conversation(
    conversation: ConversationCreate, db: Database, current_user: CurrentUser
):
    if conversation.user_friendly_link:
        link = conversation.user_friendly_link.strip()
        link = link.replace(" ", "-").lower()
        conversation.user_friendly_link = urllib.parse.quote(link)

        if db.query(models.Conversation).filter(
            models.Conversation.user_friendly_link == conversation.user_friendly_link
        ).first():
            raise HTTPException(
                status_code=409, detail="User friendly link already exists"
            )

    db_conversation = models.Conversation(
        **conversation.model_dump(), author=current_user
    )
    db.add(db_conversation)
    db.commit()

    return {"id": db_conversation.id}


@router.put("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: UUID,
    conversation: ConversationUpdate,
    db: Database,
    current_user: CurrentUser,
):
    conversation_db = db.query(models.Conversation).get(conversation_id)
    if conversation_db is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation_db.author != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in conversation.model_dump(exclude_unset=True).items():
        setattr(conversation_db, key, value)

    db.commit()

    return {"id": conversation_db.id}


@router.post("/conversations/{conversation_id}/comments")
async def create_comment(
    conversation_id: UUID,
    comment: CommentCreate,
    db: Database,
    current_user: CurrentUser,
):
    conversation = db.query(models.Conversation).get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db_comment = models.Comment(
        **comment.model_dump(), conversation=conversation, user=current_user
    )
    db.add(db_comment)
    db.commit()

    return {"id": db_comment.id}


@router.get("/conversations/{conversation_id}/comments/remaining")
async def get_next_remaining_comment(
    conversation_id: UUID,
    db: Database,
    current_user: CurrentUser,
):
    conversation = db.query(models.Conversation).get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user_votes = db.query(models.Vote).filter(models.Vote.user == current_user).all()
    user_voted_comments = {vote.comment_id for vote in user_votes}

    remaining_comment = (
        db.query(models.Comment)
        .filter(
            models.Comment.conversation == conversation,
            models.Comment.approved,
            models.Comment.user != current_user,
            models.Comment.id.notin_(user_voted_comments),
        )
        .first()
    )

    if remaining_comment is None:
        raise HTTPException(status_code=404, detail="No remaining comments found")

    return {"num_votes": len(user_voted_comments), "comment": remaining_comment}


@router.post("/comments/{comment_id}/vote")
async def vote_on_comment(
    comment_id: UUID, vote: Vote, db: Database, current_user: CurrentUser
):
    comment = db.query(models.Comment).get(comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    db_vote = (
        db.query(models.Vote)
        .filter(models.Vote.comment == comment, models.Vote.user == current_user)
        .first()
    )

    if db_vote is not None:
        db_vote.value = vote.value
    else:
        db_vote = models.Vote(**vote.model_dump(), comment=comment, user=current_user)
        db.add(db_vote)
    db.commit()

    return {"id": db_vote.id}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID, db: Database, current_user: CurrentUser
):
    conversation = db.query(models.Conversation).get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.author != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(conversation)
    db.commit()

    return {"detail": "Conversation deleted successfully", "id": conversation_id}
