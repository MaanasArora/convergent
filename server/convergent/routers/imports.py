from datetime import datetime
import pandas as pd
from typing import Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import false, true
import urllib
from convergent import models
from convergent.auth.user import CurrentUser
from convergent.database import Database
from convergent.core.routines import update_conversation_analysis
from pydantic import BaseModel


router = APIRouter()


def process_summary_file(file: UploadFile, user_id: UUID) -> models.Conversation:
    try:
        df = pd.read_csv(file.file, index_col=0, header=None).T.iloc[0]

        conversation = models.Conversation(
            id=uuid4(),
            name=df["topic"],
            description=df["conversation-description"],
            author_id=user_id,
            date_created=datetime.now(),
            is_active=False,
            user_friendly_link=None,
        )
        return conversation
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


def process_datetime(dt_str: pd.Series) -> pd.Series:
    clean = dt_str.str.replace(r" \(.*\)", "", regex=True)  # remove "(...)"
    return clean.pipe(pd.to_datetime, format="%a %b %d %Y %H:%M:%S GMT%z")


def process_comments_file(file: UploadFile, conversation_id: UUID):
    try:
        df = pd.read_csv(file.file)

        comment_ids = df["comment-id"].unique()
        author_ids = df["author-id"].unique()

        comment_ids_to_uuid = {cid: uuid4() for cid in comment_ids}
        author_ids_to_uuid = {aid: uuid4() for aid in author_ids}

        conversation_uuid = conversation_id
        comment_uuids = df["comment-id"].map(comment_ids_to_uuid)
        author_uuids = df["author-id"].map(author_ids_to_uuid)
        content = df["comment-body"]
        date_created = process_datetime(df["datetime"])

        comments = [
            models.Comment(
                id=cid,
                conversation_id=conversation_uuid,
                user_id=aid,
                content=cont,
                date_created=dt.to_pydatetime(),
            )
            for cid, aid, cont, dt in zip(
                comment_uuids, author_uuids, content, date_created
            )
        ]
        return comments, author_ids_to_uuid, comment_ids_to_uuid
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


def process_votes_file(
    file: UploadFile,
    conversation_id: UUID,
    author_ids_to_uuid: dict,
    comment_ids_to_uuid: dict,
):
    try:
        df = pd.read_csv(file.file)

        voter_ids = df["voter-id"].unique()
        voter_ids_to_uuid = {
            vid: author_ids_to_uuid.get(vid, uuid4()) for vid in voter_ids
        }

        comment_uuids = df["comment-id"].map(comment_ids_to_uuid)
        voter_uuids = df["voter-id"].map(voter_ids_to_uuid)
        values = df["vote"]
        date_created = process_datetime(df["datetime"])

        votes = [
            models.Vote(
                id=uuid4(),
                comment_id=cid,
                user_id=uid,
                value=val,
                date_created=dt.to_pydatetime(),
            )
            for cid, uid, val, dt in zip(
                comment_uuids, voter_uuids, values, date_created
            )
        ]
        return votes, voter_ids_to_uuid
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@router.post("/conversations/import")
async def import_data(
    files: list[UploadFile],
    db: Database,
    current_user: CurrentUser,
    refresh_analysis: Optional[bool] = True,
):
    summary_file = None
    comments_file = None
    votes_history_file = None

    for file in files:
        if file.filename is None:
            continue

        if file.filename.endswith("summary.csv"):
            summary_file = file
        elif file.filename.endswith("comments.csv"):
            comments_file = file
        elif file.filename.endswith("votes.csv"):
            votes_history_file = file

    if summary_file is None:
        raise HTTPException(
            status_code=400, detail="Summary file is required for import."
        )

    conversation = process_summary_file(summary_file, current_user.id)
    db.add(conversation)

    if comments_file is not None:
        comments, author_uuids, comment_ids_to_uuid = process_comments_file(
            comments_file, conversation.id
        )

        if votes_history_file is None:
            raise HTTPException(
                status_code=400,
                detail="Votes file is required when importing comments.",
            )

        votes, voter_uuids = process_votes_file(
            votes_history_file, conversation.id, author_uuids, comment_ids_to_uuid
        )

        db.add_all(comments)
        db.add_all(votes)

        # create users for authors / voters
        unique_user_ids = set(voter_uuids.values()).union(set(author_uuids.values()))
        for user_id in unique_user_ids:
            user = models.User(
                id=user_id, username=f"user_{user_id.hex[:8]}", hashed_password=""
            )
            db.add(user)

        db.commit()

    if refresh_analysis:
        update_conversation_analysis(conversation, db)

    return {"status": "success"}


@router.delete("/conversations/{conversation_id}/import")
async def delete_imported_conversation(
    conversation_id: UUID, db: Database, current_user: CurrentUser
):
    conversation = db.query(models.Conversation).get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.author != current_user:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this conversation"
        )

    # delete comments, votes, users, and analysis related to this conversation
    db.query(models.UserPca).filter(
        models.UserPca.conversation_id == conversation_id
    ).delete(synchronize_session=False)

    db.query(models.UserCluster).filter(
        models.UserCluster.conversation_id == conversation_id
    ).delete(synchronize_session=False)

    db.query(models.Vote).filter(
        models.Vote.comment_id.in_(
            db.query(models.Comment.id).filter(
                models.Comment.conversation_id == conversation_id
            )
        )
    ).delete(synchronize_session=False)

    db.query(models.Comment).filter(
        models.Comment.conversation_id == conversation_id
    ).delete(synchronize_session=False)

    db.query(models.User).filter(
        models.User.id.in_(
            db.query(models.Comment.user_id).filter(
                models.Comment.conversation_id == conversation_id
            )
        )
    ).delete(synchronize_session=False)

    db.delete(conversation)
    db.commit()

    return {"status": "deleted"}
