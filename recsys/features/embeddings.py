import pandas as pd
import tensorflow as tf


def preprocess(train_df: pd.DataFrame, candidate_features: list) -> pd.DataFrame:
    # Select the candidate features from the training DataFrame
    item_df = train_df[candidate_features]

    # Drop duplicate rows based on the 'artwork_id' column to get unique candidate items
    item_df.drop_duplicates(subset="artwork_id", inplace=True)

    return item_df


def embed(df: pd.DataFrame, candidate_model) -> pd.DataFrame:
    ds = tf.data.Dataset.from_tensor_slices({col: df[col] for col in df})

    candidate_embeddings = ds.batch(2048).map(
        lambda x: (x["artwork_id"], candidate_model(x))
    )

    all_artwork_ids = tf.concat([batch[0] for batch in candidate_embeddings], axis=0)
    all_embeddings = tf.concat([batch[1] for batch in candidate_embeddings], axis=0)

    all_artwork_ids = all_artwork_ids.numpy().astype(str).tolist()
    all_embeddings = all_embeddings.numpy().tolist()

    embeddings_df = pd.DataFrame(
        {
            "artwork_id": all_artwork_ids,
            "embeddings": all_embeddings,
        }
    )

    return embeddings_df