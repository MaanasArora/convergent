from dataclasses import dataclass
from typing import Annotated
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
from convergent.core.routines import get_vote_matrix, update_conversation_analysis


router = APIRouter(prefix="/analysis")


class CommentRepresentativeness(BaseModel):
    group_id: int
    representativeness: float | None


class CommentVoteProbabilities(BaseModel):
    agree: float
    disagree: float
    skip: float


class CommentAnalysis(BaseModel):
    comment_id: UUID
    content: str
    total_votes: int
    consensus: float
    participation_rate: float
    vote_probabilities: CommentVoteProbabilities
    representativeness: list[CommentRepresentativeness]


class GroupCommentRepresentativeness(BaseModel):
    group_id: int
    comment_id: UUID
    content: str
    agree_percentage: float | None = None
    representativeness: float | None = None


class GroupAnalysis(BaseModel):
    group_id: int
    users: list[UUID]


@dataclass
class ConversationAnalysisRawData:
    conversation_id: UUID
    comment_ids: list[UUID]
    user_ids: list[UUID]
    vote_matrix: np.ndarray
    cluster_labels: np.ndarray | None = None


class ConversationAnalysis(BaseModel):
    conversation_id: UUID
    comment_ids: list[UUID]
    user_ids: list[UUID]

    comments: list[CommentAnalysis] | None = None
    groups: list[GroupAnalysis] | None = None


class GroupAnalysisResponse(BaseModel):
    group_id: int
    users: list[UUID]
    representative_comments: list[GroupCommentRepresentativeness] | None = None


class CommentAnalysisResponse(BaseModel):
    comment_id: UUID
    content: str
    total_votes: int
    consensus: float
    participation_rate: float
    vote_probabilities: CommentVoteProbabilities
    representativeness: list[CommentRepresentativeness]


class ConversationAnalysisResponse(BaseModel):
    conversation_id: UUID
    comment_ids: list[UUID]
    user_ids: list[UUID]

    comments_by_consensus: list[CommentAnalysisResponse] | None = None
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


def get_cluster_labels(
    db: Database, conversation: models.Conversation, user_ids: list[UUID]
):
    user_clusters = conversation.clusters
    if user_clusters is None:
        return None

    cluster_map = {cluster.user.id: cluster.cluster for cluster in user_clusters}
    return np.array([cluster_map.get(user_id, -1) for user_id in user_ids])


def get_conversation_analysis_raw_data(
    db: Database, conversation: models.Conversation
) -> ConversationAnalysisRawData:
    vote_matrix, user_idx, comment_idx = get_vote_matrix(conversation)

    users = sorted(user_idx, key=lambda uid: user_idx[uid])
    comments = sorted(comment_idx.keys(), key=lambda cid: comment_idx[cid])

    user_ids = [user.id for user in users]
    comment_ids = [comment.id for comment in comments]

    cluster_labels = get_cluster_labels(db, conversation, user_ids)

    return ConversationAnalysisRawData(
        conversation_id=conversation.id,
        comment_ids=comment_ids,
        user_ids=user_ids,
        vote_matrix=vote_matrix,
        cluster_labels=cluster_labels,
    )


def get_conversation_groups(db: Database, raw_data: ConversationAnalysisRawData):
    if raw_data.cluster_labels is None:
        return []

    groups = {}
    for user_id, cluster_id in zip(raw_data.user_ids, raw_data.cluster_labels):
        if cluster_id == -1:
            continue
        if cluster_id not in groups:
            groups[cluster_id] = {}
            groups[cluster_id]["users"] = []
            groups[cluster_id]["representative_comments"] = []
        groups[cluster_id]["users"].append(user_id)

    return [
        GroupAnalysis.model_validate(
            {
                "group_id": cluster_id,
                **groups[cluster_id],
            }
        )
        for cluster_id in groups
    ]


def get_comment_analysis(
    db: Database,
    comment: models.Comment,
    raw_data: ConversationAnalysisRawData,
):
    if comment.id not in raw_data.comment_ids:
        raise ValueError("Comment ID not found in raw data")

    comment_idx = raw_data.comment_ids.index(comment.id)
    votes = raw_data.vote_matrix[:, comment_idx]

    consensus = get_comment_consensus(votes, raw_data.cluster_labels)
    if np.isnan(consensus):
        consensus = 0.0
    if consensus is None:
        consensus = 0.0
    participation_rate = calculate_participation_rate(votes)
    vote_probabilities = get_comment_vote_probabilities(votes)

    representativeness = []
    if raw_data.cluster_labels is not None:
        unique_clusters = set(raw_data.cluster_labels)
        for cluster_id in unique_clusters:
            if cluster_id == -1:
                continue
            rep = get_group_comment_representativeness(
                votes, raw_data.cluster_labels, cluster_id
            )
            representativeness.append(
                CommentRepresentativeness(
                    group_id=int(cluster_id), representativeness=rep
                )
            )

    return CommentAnalysis(
        comment_id=comment.id,
        content=comment.content,
        total_votes=int(np.sum(~np.isnan(votes))),
        consensus=float(consensus),
        participation_rate=participation_rate,
        vote_probabilities=vote_probabilities,
        representativeness=representativeness,
    )


def get_conversation_comments(
    db: Database,
    conversation: models.Conversation,
    raw_data: ConversationAnalysisRawData,
) -> list[CommentAnalysis]:
    comments = conversation.comments
    comment_map = {comment.id: comment for comment in comments}

    comment_analyses = []
    for idx, comment_id in enumerate(raw_data.comment_ids):
        comment = comment_map.get(comment_id)
        if comment is None:
            continue

        comment_analysis = get_comment_analysis(db, comment, raw_data)
        comment_analyses.append(comment_analysis)

    return comment_analyses


@router.put("/conversation/{conversation_id}/refresh", status_code=204)
def refresh_conversation_analysis(
    conversation_id: UUID, current_user: CurrentUser, db: Database
):
    conversation = db.get(models.Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to refresh this conversation"
        )

    update_conversation_analysis(conversation, db)
    return {"status": "completed"}


def process_comment_analyses_by_consensus(
    comments: list[CommentAnalysis],
) -> list[CommentAnalysisResponse]:
    sorted_comments = sorted(
        comments,
        key=lambda x: (x.consensus is not None, x.consensus),
        reverse=True,
    )

    return [
        CommentAnalysisResponse.model_validate(comment, from_attributes=True)
        for comment in sorted_comments
    ]


def process_group_representative_comments(
    group: GroupAnalysis,
    comments: list[CommentAnalysis],
    raw_data: ConversationAnalysisRawData,
) -> list[GroupCommentRepresentativeness]:
    if not comments or group.group_id is None:
        return []

    if raw_data.cluster_labels is None:
        return []

    representative_comments = []
    for comment in comments:
        for rep in comment.representativeness:
            if rep.group_id == group.group_id:
                comment_id_to_idx = {
                    cid: idx for idx, cid in enumerate(raw_data.comment_ids)
                }
                user_indices = [
                    i
                    for i, cluster_id in enumerate(raw_data.cluster_labels)
                    if cluster_id == group.group_id
                ]

                agree_percentage = None
                if comment.comment_id in comment_id_to_idx:
                    comment_idx = comment_id_to_idx[comment.comment_id]
                    votes = raw_data.vote_matrix[user_indices, comment_idx]
                    total_votes = len(votes)
                    agree_votes = np.sum(votes == 1)
                    agree_percentage = (
                        agree_votes / total_votes if total_votes > 0 else None
                    )

                representative_comments.append(
                    GroupCommentRepresentativeness(
                        group_id=group.group_id,
                        comment_id=comment.comment_id,
                        content=comment.content,
                        agree_percentage=agree_percentage,
                        representativeness=rep.representativeness,
                    )
                )

    representative_comments.sort(
        key=lambda x: (x.representativeness is not None, x.representativeness),
        reverse=True,
    )

    return representative_comments


def process_analysis_response(
    analysis: ConversationAnalysis,
    raw_data: ConversationAnalysisRawData,
    params: dict = {},
) -> ConversationAnalysisResponse:
    comments_by_consensus = None
    if analysis.comments is not None:
        comments_by_consensus = process_comment_analyses_by_consensus(analysis.comments)

    processed_groups = [
        GroupAnalysisResponse.model_validate(group, from_attributes=True)
        for group in (analysis.groups or [])
    ]
    if analysis.groups is not None and analysis.comments is not None:
        for idx, group in enumerate(analysis.groups):
            representative_comments = process_group_representative_comments(
                group, analysis.comments, raw_data
            )
            processed_groups[idx].representative_comments = representative_comments

    num_representative_comments = params.get("num_representative_comments", 3)
    if num_representative_comments is not None:
        for idx, group in enumerate(processed_groups):
            if group.representative_comments is not None:
                processed_groups[idx].representative_comments = (
                    group.representative_comments[:num_representative_comments]
                )

    # increment group ID by 1 for frontend compatibility
    for idx, group in enumerate(processed_groups):
        processed_groups[idx].group_id = group.group_id + 1

    return ConversationAnalysisResponse(
        conversation_id=analysis.conversation_id,
        comment_ids=analysis.comment_ids,
        user_ids=analysis.user_ids,
        comments_by_consensus=comments_by_consensus,
        groups=processed_groups,
    )


@router.get(
    "/conversation/{conversation_id}", response_model=ConversationAnalysisResponse
)
def analyze_conversation(
    conversation_id: UUID,
    current_user: CurrentUser,
    db: Database,
    refresh: bool = True,
    num_representative_comments: int = 3,
):
    conversation = db.get(models.Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this conversation"
        )

    if refresh:
        update_conversation_analysis(conversation, db)

    raw_data = get_conversation_analysis_raw_data(db, conversation)
    comments = get_conversation_comments(db, conversation, raw_data)
    groups = get_conversation_groups(db, raw_data)

    analysis = ConversationAnalysis(
        conversation_id=conversation.id,
        comment_ids=raw_data.comment_ids,
        user_ids=raw_data.user_ids,
        comments=comments,
        groups=groups,
    )

    params = {"num_representative_comments": num_representative_comments}

    return process_analysis_response(analysis, raw_data, params)
