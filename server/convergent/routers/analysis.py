from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from convergent import models
from convergent.auth.user import CurrentUser
from convergent.database import Database
from pydantic import BaseModel
import numpy as np
from convergent_engine.math import (
    get_comment_consensus,
    get_group_comment_representativeness,
)
from convergent.core.routines import get_vote_matrix


router = APIRouter(prefix="/analysis")


class CommentRepresentativeness(BaseModel):
    group_id: int
    representativeness: float | None


class CommentVoteProbabilities(BaseModel):
    agree: float
    disagree: float
    skip: float


class CommentAnalysisResponse(BaseModel):
    comment_id: UUID
    content: str
    total_votes: int
    consensus: float
    participation_rate: float
    vote_probabilities: CommentVoteProbabilities
    representativeness: list[CommentRepresentativeness]


class GroupAnalysisResponse(BaseModel):
    group_id: int
    users: list[UUID]


class ConversationAnalysisResponse(BaseModel):
    conversation_id: UUID
    comment_ids: list[UUID]
    user_ids: list[UUID]

    comments: list[CommentAnalysisResponse] | None = None
    groups: list[GroupAnalysisResponse] | None = None


def get_comment_vote_probabilities(votes: np.ndarray):
    total_votes = np.sum(~np.isnan(votes))
    if total_votes == 0:
        return CommentVoteProbabilities(agree=0.0, disagree=0.0, skip=0.0)

    agree = np.sum(votes == 1)
    disagree = np.sum(votes == -1)
    skip = np.sum(votes == 0)

    return CommentVoteProbabilities(
        agree=agree / total_votes,
        disagree=disagree / total_votes,
        skip=skip / total_votes,
    )


def calculate_participation_rate(votes: np.ndarray):
    total_votes = np.sum(~np.isnan(votes))
    if votes.size == 0:
        return 0.0
    return total_votes / votes.size


def get_conversation_groups(
    db: Database, conversation_id: UUID
) -> list[GroupAnalysisResponse]:
    group_ids = (
        db.query(models.UserCluster.cluster)
        .filter(models.UserCluster.conversation_id == conversation_id)
        .distinct()
        .all()
    )
    group_ids = [gid[0] for gid in group_ids]

    groups = []
    for group_id in group_ids:
        users = (
            db.query(models.UserCluster.user_id)
            .filter(
                models.UserCluster.conversation_id == conversation_id,
                models.UserCluster.cluster == group_id,
            )
            .all()
        )
        user_ids = [u[0] for u in users]
        groups.append(GroupAnalysisResponse(group_id=group_id, users=user_ids))

    return groups


def get_comment_representativeness(
    votes: np.ndarray, cluster_labels: np.ndarray
) -> list[CommentRepresentativeness]:
    representativeness = []
    unique_clusters = np.unique(cluster_labels)
    for cluster_id in unique_clusters:
        rep = get_group_comment_representativeness(votes, cluster_labels, cluster_id)
        representativeness.append(
            CommentRepresentativeness(group_id=int(cluster_id), representativeness=rep)
        )
    return representativeness


def get_comment_analysis(
    db: Database,
    conversation_id: UUID,
    comment: models.Comment,
    cluster_labels: np.ndarray | None,
) -> CommentAnalysisResponse:
    conversation = db.get(models.Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    votes, user_ids, comment_ids = get_vote_matrix(conversation)
    if comment.id not in comment_ids:
        raise HTTPException(status_code=404, detail="Comment not found in conversation")
    
    comment_index = [i for i, cid in enumerate(comment_ids) if cid == comment.id][0]
    votes = votes[:, comment_index]

    consensus = get_comment_consensus(votes, cluster_labels)
    participation_rate = calculate_participation_rate(votes)
    vote_probabilities = get_comment_vote_probabilities(votes)
    consensus = float(consensus) if consensus is not None else 0.0

    if cluster_labels is not None:
        representativeness = get_comment_representativeness(votes, cluster_labels)
    else:
        representativeness = []

    total_votes = int(np.sum(~np.isnan(votes)))

    return CommentAnalysisResponse(
        comment_id=comment.id,
        content=comment.content,
        total_votes=total_votes,
        consensus=consensus,
        participation_rate=participation_rate,
        vote_probabilities=vote_probabilities,
        representativeness=representativeness,
    )