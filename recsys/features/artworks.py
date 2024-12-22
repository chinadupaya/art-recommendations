import contextlib
import io
import sys

import polars as pl
from tqdm.auto import tqdm
from sentence_transformers import SentenceTransformer

def compute_features_artworks(df: pl.DataFrame) -> pl.DataFrame:
    """
    Prepares the input DataFrame by creating new features and dropping specific columns.
    Parameters:
    - df (pl.DataFrame): Input DataFrame.
    Returns:
    - pl.DataFrame: Processed DataFrame with new features and specific columns dropped.
    """
    # Create new columns
    # df = df.with_columns(
    #     [
    #         get_article_id(df).alias("article_id"),
    #         create_prod_name_length(df).alias("prod_name_length"),
    #         pl.struct(df.columns)
    #         .map_elements(create_article_description)
    #         .alias("article_description"),
    #     ]
    # )

    # # Add full image URLs.
    # df = df.with_columns(image_url=pl.col("article_id").map_elements(get_image_url))

    # # Drop columns with null values
    # df = df.select([col for col in df.columns if not df[col].is_null().any()])

    # Remove  column
    df = df.rename({"id": "artwork_id"})
    columns_to_drop = ["artists_link", "genes_link", "similar_link"]
    existing_columns = df.columns
    columns_to_keep = [col for col in existing_columns if col not in columns_to_drop]


    return df.select(columns_to_keep)


def generate_embeddings_for_dataframe(
    df: pl.DataFrame, text_column: str, model: SentenceTransformer, batch_size: int = 32
) -> pl.DataFrame:
    """
    Generate embeddings for a text column in a Polars DataFrame.

    Args:
    df (pl.DataFrame): Input Polars DataFrame
    text_column (str): Name of the column containing text to embed
    model (SentenceTransformer): SentenceTransformer embedding model to use
    batch_size (int): Number of samples run at once through the embedding model

    Returns:
    pl.DataFrame: DataFrame with a new 'embedding' column
    """

    @contextlib.contextmanager
    def suppress_stdout():
        new_stdout = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = new_stdout
        try:
            yield new_stdout
        finally:
            sys.stdout = old_stdout

    total_rows = len(df)
    pbar = tqdm(total=total_rows, desc="Generating embeddings")

    # Create a new column with embeddings
    texts = df[text_column].to_list()

    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        with suppress_stdout():
            batch_embeddings = model.encode(
                batch_texts, device=model.device, show_progress_bar=False
            )
        all_embeddings.extend(batch_embeddings.tolist())
        pbar.update(len(batch_texts))

    df_with_embeddings = df.with_columns(embeddings=pl.Series(all_embeddings))

    pbar.close()

    return df_with_embeddings
