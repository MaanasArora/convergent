import numpy as np
from convergent_engine.math import (
    decompose_votes,
    cluster_users,
    get_comment_consensus,
    get_group_comment_representativeness,
)


def test_decompose_votes():
    vote_matrix = np.array([[1, 2, np.nan], [3, np.nan, 4], [np.nan, 5, 6]])
    transformed = decompose_votes(vote_matrix)

    assert transformed.shape == (3, 2)
    assert not np.isnan(transformed).any()


def test_cluster_users():
    reduced = np.array([[1, 2], [1.1, 2.1], [3, 4], [3.1, 4.1]])
    kmeans = cluster_users(reduced, random_state=42)

    assert kmeans is not None
    assert len(np.unique(kmeans.labels_)) == 2


def test_get_comment_representativeness():
    votes_matrix = np.array([[1, 0, 1], [0, 1, 1], [1, 1, 0], [np.nan, 1, 1]])
    cluster_labels = np.array([0, 0, 1, 1])

    representativeness = get_group_comment_representativeness(
        votes_matrix[:, 0], cluster_labels, cluster_index=0
    )
    assert representativeness is not None
    assert np.isclose(representativeness, 0.75, atol=1e-5)


def test_get_comment_consensus():
    votes_matrix = np.array([[1, 0, 1], [0, 1, 1], [1, 1, 0]])
    cluster_labels = np.array([0, 0, 1])

    consensus_group_aware = get_comment_consensus(
        votes_matrix[:, 0], cluster_labels=cluster_labels, kind="group_aware"
    )
    consensus_simple = get_comment_consensus(votes_matrix[:, 0], kind="simple")

    assert np.isclose(consensus_group_aware, 0.33333, atol=1e-5)
    assert np.isclose(consensus_simple, 0.66666, atol=1e-5)
