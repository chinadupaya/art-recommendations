import hopsworks
import pandas as pd
from hsfs import embedding
from loguru import logger

from recsys.config import settings
from recsys.hopsworks_integration import constants
from recsys.features.transactions import month_cos, month_sin


import os
def get_feature_store():
    # os.environ["HOPSWORKS_API_KEY"]
    if settings.HOPSWORKS_API_KEY:
        logger.info("Loging to Hopsworks using HOPSWORKS_API_KEY env var.")
        project = hopsworks.login(
            api_key_value=settings.HOPSWORKS_API_KEY.get_secret_value()
            # api_key_value=
        )
    else:
        logger.info("Login to Hopsworks using cached API key.")
        project = hopsworks.login()

    return project, project.get_feature_store()


########################
#### Feature Groups ####
########################


def create_users_feature_group(fs, df: pd.DataFrame, online_enabled: bool = True):
    users_fg = fs.get_or_create_feature_group(
        name="users",
        description="Users data including age and gender",
        version=1,
        primary_key=["user_id"],
        online_enabled=online_enabled,
    )
    users_fg.insert(df, wait=True)

    for desc in constants.customer_feature_descriptions:
        users_fg.update_feature_description(desc["name"], desc["description"])

    return users_fg


def create_artworks_feature_group(
    fs,
    df: pd.DataFrame,
    artworks_description_embedding_dim: int,
    online_enabled: bool = True,
):
    # Create the Embedding Index for the articles description embedding.
    emb = embedding.EmbeddingIndex()
    emb.add_embedding("embeddings", artworks_description_embedding_dim)

    artworks_fg = fs.get_or_create_feature_group(
        name="artworks",
        version=1,
        description="Artworks data including category, description, and title",
        primary_key=["artwork_id"],
        online_enabled=online_enabled,
        features=constants.artwork_feature_description,
        embedding_index=emb,
    )
    artworks_fg.insert(df, wait=True)

    return artworks_fg


def create_transactions_feature_group(
    fs, df: pd.DataFrame, online_enabled: bool = True
):
    trans_fg = fs.get_or_create_feature_group(
        name="transactions",
        version=1,
        description="Transactions data including customer, artwork, and date",
        primary_key=["user_id", "artwork_id"],
        online_enabled=online_enabled,
        event_time="t_dat",
    )
    trans_fg.insert(df, wait=True)

    for desc in constants.transactions_feature_descriptions:
        trans_fg.update_feature_description(desc["name"], desc["description"])

    return trans_fg


def create_interactions_feature_group(
    fs, df: pd.DataFrame, online_enabled: bool = True
):
    interactions_fg = fs.get_or_create_feature_group(
        name="interactions",
        version=1,
        description="User interactions with artworks including likes, clicks, and ignores. Used for building recommendation systems and analyzing user behavior.",
        primary_key=["user_id", "artwork_id"],
        online_enabled=online_enabled,
        event_time="t_dat",
    )

    interactions_fg.insert(
        df,
        wait=True,
    )

    for desc in constants.interactions_feature_descriptions:
        interactions_fg.update_feature_description(desc["name"], desc["description"])

    return interactions_fg


def create_ranking_feature_group(
    fs, df: pd.DataFrame, parents: list, online_enabled: bool = True
):
    rank_fg = fs.get_or_create_feature_group(
        name="ranking",
        version=1,
        description="Derived feature group for ranking",
        primary_key=["customer_id", "artwork_id"],
        parents=parents,
        online_enabled=online_enabled,
    )
    rank_fg.insert(df, wait=True)

    for desc in constants.ranking_feature_descriptions:
        rank_fg.update_feature_description(desc["name"], desc["description"])

    return rank_fg


def create_candidate_embeddings_feature_group(
    fs, df: pd.DataFrame, online_enabled: bool = True
):
    embedding_index = embedding.EmbeddingIndex()

    embedding_index.add_embedding(
        "embeddings",  # Embeddings feature name
        settings.TWO_TOWER_MODEL_EMBEDDING_SIZE,
    )

    candidate_embeddings_fg = fs.get_or_create_feature_group(
        name="candidate_embeddings",
        embedding_index=embedding_index,  # Specify the Embedding Index
        primary_key=["artwork_id"],
        version=1,
        description="Embeddings for each artwork.",
        online_enabled=online_enabled,
    )
    candidate_embeddings_fg.insert(df, wait=True)

    return candidate_embeddings_fg

#########################
##### Feature Views #####
#########################


# def create_retrieval_feature_view(fs):
#     trans_fg = fs.get_feature_group(name="transactions", version=1)
#     customers_fg = fs.get_feature_group(name="customers", version=1)
#     articles_fg = fs.get_feature_group(name="articles", version=1)

#     # You'll need to join these three data sources to make the data compatible
#     # with out retrieval model. Recall that each row in the `transactions` feature group
#     # relates information about which customer bought which item.
#     # You'll join this feature group with the `customers` and `articles` feature groups
#     # to inject customer and item features into each row.
#     selected_features = (
#         trans_fg.select(
#             ["customer_id", "article_id", "t_dat", "price", "month_sin", "month_cos"]
#         )
#         .join(
#             customers_fg.select(["age", "club_member_status", "age_group"]),
#             on="customer_id",
#         )
#         .join(
#             articles_fg.select(["garment_group_name", "index_group_name"]),
#             on="article_id",
#         )
#     )

#     feature_view = fs.get_or_create_feature_view(
#         name="retrieval",
#         query=selected_features,
#         version=1,
#     )

#     return feature_view


# def create_ranking_feature_views(fs):
#     customers_fg = fs.get_feature_group(
#         name="customers",
#         version=1,
#     )

#     articles_fg = fs.get_feature_group(
#         name="articles",
#         version=1,
#     )

#     rank_fg = fs.get_feature_group(
#         name="ranking",
#         version=1,
#     )

#     trans_fg = fs.get_feature_group(
#         name="transactions",
#         version=1)

#     selected_features_customers = customers_fg.select_all()
#     fs.get_or_create_feature_view(
#         name="customers",
#         query=selected_features_customers,
#         version=1,
#     )

#     selected_features_articles = articles_fg.select_except(["embeddings"])
#     fs.get_or_create_feature_view(
#         name="articles",
#         query=selected_features_articles,
#         version=1,
#     )

#     # Select features
#     selected_features_ranking = rank_fg.select_except(["customer_id", "article_id"]).join(trans_fg.select(["month_sin", "month_cos"]))
#     feature_view_ranking = fs.get_or_create_feature_view(
#         name="ranking",
#         query=selected_features_ranking,
#         labels=["label"],
#         version=1,
#     )

#     return feature_view_ranking


def create_candidate_embeddings_feature_view(fs, fg):
    feature_view = fs.get_or_create_feature_view(
        name="candidate_embeddings",
        version=1,
        description="Embeddings of each artwork",
        query=fg.select(["id"]),
    )

    return feature_view
