import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


random_state = 42


def decompose_votes(vote_matrix: np.ndarray, random_state: int = random_state):
    pca = PCA(n_components=2, random_state=random_state, svd_solver="covariance_eigh")

    vote_matrix_nonan = np.nan_to_num(vote_matrix, nan=0)
    transformed = pca.fit_transform(vote_matrix_nonan)

    total_votes = np.sum(~np.isnan(vote_matrix_nonan), axis=1)
    vote_scale = np.sum(~np.isnan(vote_matrix_nonan), axis=1)
    vote_scale = np.sqrt(total_votes / (vote_scale + 1e-10))

    return transformed * vote_scale[:, None]


def cluster_users(
    reduced: np.ndarray, random_state: int = random_state, n_init: int = 100
):
    best_silhouette = -1
    best_kmeans = None
    for n_clusters in range(2, min(4, len(reduced))):
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=n_init)
        kmeans.fit(reduced)
        silhouette = silhouette_score(
            reduced, kmeans.labels_, random_state=random_state
        )
        if silhouette > best_silhouette:
            best_silhouette = silhouette
            best_kmeans = kmeans

    return best_kmeans


def get_group_comment_representativeness(
    comment_votes: np.ndarray, cluster_labels: np.ndarray, cluster_index: int
):
    if cluster_index == -1:
        return None

    cluster_votes = comment_votes[cluster_labels == cluster_index]
    not_cluster_votes = comment_votes[cluster_labels != cluster_index]

    cluster_agree = np.sum(cluster_votes == 1)
    not_cluster_agree = np.sum(not_cluster_votes == 1)

    cluster_total = np.sum(~np.isnan(cluster_votes))
    not_cluster_total = np.sum(~np.isnan(not_cluster_votes))

    cluster_agree_prob = (1 + cluster_agree) / (2 + cluster_total)
    not_cluster_agree_prob = (1 + not_cluster_agree) / (2 + not_cluster_total)

    return cluster_agree_prob / not_cluster_agree_prob


def get_comment_consensus(
    comment_votes: np.ndarray,
    cluster_labels: np.ndarray | None = None,
    kind="group_aware",
):
    if kind == "group_aware":
        if cluster_labels is None:
            raise ValueError(
                "Cluster labels must be provided for group-aware consensus."
            )

        cluster_agree_probs = np.zeros(len(np.unique(cluster_labels)))

        for cluster in np.unique(cluster_labels):
            if cluster == -1:
                continue

            cluster_votes = comment_votes[cluster_labels == cluster]

            if len(cluster_votes) == 0 or np.all(np.isnan(cluster_votes)):
                cluster_agree_probs[cluster] = 0.5
                continue

            agree_vote_count = np.sum(cluster_votes == 1)
            total_vote_count = np.sum(~np.isnan(cluster_votes))

            cluster_agree_probs[cluster] = (1 + agree_vote_count) / (
                2 + total_vote_count
            )

        return np.prod(cluster_agree_probs)

    elif kind == "simple":
        return np.nanmean(comment_votes == 1)

    else:
        raise ValueError(f"Unknown kind: {kind}. Use 'group_aware' or 'simple'.")
