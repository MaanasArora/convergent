from sqlalchemy.orm import Session
from convergent import models
import numpy as np
from convergent_engine import decompose_votes, cluster_users


def get_vote_matrix(conversation: models.Conversation):
    comments = conversation.comments

    users = set()
    for comment in comments:
        for vote in comment.votes:
            users.add(vote.user)

    vote_matrix = np.full((len(users), len(comments)), fill_value=np.nan)
    user_index = {user: i for i, user in enumerate(users)}
    comment_index = {comment: i for i, comment in enumerate(comments)}

    for comment in comments:
        for vote in comment.votes:
            vote_matrix[user_index[vote.user], comment_index[comment]] = vote.value

    return vote_matrix, user_index, comment_index


def update_conversation_analysis(conversation: models.Conversation, db: Session):
    vote_matrix, user_index, _ = get_vote_matrix(conversation)
    if min(vote_matrix.shape) < 2:
        return

    pca = decompose_votes(vote_matrix)
    if len(np.unique(vote_matrix)) <= 1:
        # Not enough diversity in votes to form clusters
        cluster = None
    else:
        cluster = cluster_users(pca)
    
    index_to_user = {i: user for user, i in user_index.items()}

    for i, pca_values in enumerate(pca):
        user_pca = (
            db.query(models.UserPca)
            .filter(
                models.UserPca.user == index_to_user[i],
                models.UserPca.conversation == conversation,
            )
            .first()
        )
        if user_pca is None:
            user_pca = models.UserPca(user=index_to_user[i], conversation=conversation)
            db.add(user_pca)
        user_pca.x, user_pca.y = pca_values.astype(float).tolist()

    if cluster is None:
        db.commit()
        return

    for i, label in enumerate(cluster.labels_):
        user_cluster = (
            db.query(models.UserCluster)
            .filter(
                models.UserCluster.user == index_to_user[i],
                models.UserCluster.conversation == conversation,
            )
            .first()
        )
        if user_cluster is None:
            user_cluster = models.UserCluster(
                user=index_to_user[i], conversation=conversation
            )
            db.add(user_cluster)
        user_cluster.cluster = int(label)

    db.commit()
