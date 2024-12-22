import polars as pl

def compute_ranking_dataset2(trans_df, artworks_df2, users_df) -> pl.DataFrame:
    # Read data from the feature groups
    trans_df = trans_df[
        ["artwork_id", "user_id"]
    ]
    artworks_df = artworks_df2.select(pl.exclude(
        ["description", "embeddings", "thumbnail_link"]
    ))
    users_df = users_df[["user_id", "age"]]

    # Convert artwork_id to string in both dataframes before joining
    trans_df = trans_df.with_columns(pl.col("artwork_id").cast(pl.Utf8))
    artworks_df = artworks_df.with_columns(pl.col("artwork_id").cast(pl.Utf8))

    # Merge operations
    df = trans_df.join(artworks_df, on="artwork_id", how="left")
    df = df.join(users_df, on="user_id", how="left")

    # Select query features
    query_features = ["user_id", "age", "artwork_id"]
    df = df.select(query_features)

    # Create positive pairs
    positive_pairs = df.clone()

    # Calculate number of negative pairs
    n_neg = len(positive_pairs) * 10

    # Create negative pairs DataFrame
    artwork_ids = (df.select("artwork_id")
                    .unique()
                    .sample(n=n_neg, with_replacement=True, seed=2)
                    .get_column("artwork_id"))
    
    user_ids = (df.select("user_id")
                     .sample(n=n_neg, with_replacement=True, seed=3)
                     .get_column("user_id"))

    other_features = (df.select(["age"])
                       .sample(n=n_neg, with_replacement=True, seed=4))

    # Construct negative pairs
    negative_pairs = pl.DataFrame({
        "artwork_id": artwork_ids,
        "user_id": user_ids,
        "age": other_features.get_column("age"),
    })

    # Add labels
    positive_pairs = positive_pairs.with_columns(pl.lit(1).alias("label"))
    negative_pairs = negative_pairs.with_columns(pl.lit(0).alias("label"))

    # Concatenate positive and negative pairs
    ranking_df = pl.concat([
        positive_pairs,
        negative_pairs.select(positive_pairs.columns)
    ])

    # Process item features
    item_df = artworks_df2
    
    # Convert artwork_id to string in item_df before final join
    item_df = item_df.with_columns(pl.col("artwork_id").cast(pl.Utf8))
    
    # Keep unique artwork_ids and select columns
    item_df = (
        item_df.unique(subset=["artwork_id"])
        .select([
            "artwork_id",
            "title",
            "description",
            "category"
            # "graphical_appearance_name",
            # "colour_group_name",
            # "perceived_colour_value_name",
            # "perceived_colour_master_name",
            # "department_name",
            # "index_name",
            # "index_group_name",
            # "section_name",
            # "garment_group_name",
        ])
    )

    # Final merge with item features
    ranking_df = ranking_df.join(item_df, on="artwork_id", how="left")

    return ranking_df
