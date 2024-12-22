import numpy as np
import polars as pl
from tqdm import tqdm


def generate_interaction_data(trans_df):
    # Pre-compute unique values once
    unique_users = trans_df["user_id"].unique()
    all_artworks = trans_df["artwork_id"].unique()
    all_artworks_set = set(all_artworks)

    interactions = []

    def generate_timestamps(base_timestamp, count, min_hours, max_hours):
        hours = np.random.randint(min_hours, max_hours, size=count)
        return base_timestamp - (hours * 3600000)

    # Ratios to ensure more realistic interactions
    CLICK_BEFORE_PURCHASE_PROB = 0.9
    MIN_IGNORES = 40
    MAX_IGNORES = 60
    MIN_EXTRA_CLICKS = 5
    MAX_EXTRA_CLICKS = 8
    EXTRA_CLICKS_PROB = 0.95

    chunk_size = 1000
    for chunk_start in tqdm(
        range(0, len(unique_users), chunk_size), desc="Processing user chunks"
    ):
        chunk_end = min(chunk_start + chunk_size, len(unique_users))
        chunk_users = unique_users[chunk_start:chunk_end]

        chunk_transactions = trans_df.filter(
            pl.col("user_id").is_in(chunk_users)
        )

        for user_id in chunk_users:
            user_likes = chunk_transactions.filter(
                pl.col("user_id") == user_id
            )

            if len(user_likes) == 0:
                continue

            user_artworks = {"liked": set(), "clicked": set(), "ignored": set()}
            last_like_timestamp = user_likes["t_dat"].max()

            # Generate more ignores first
            num_ignores = np.random.randint(MIN_IGNORES, MAX_IGNORES)
            available_artworks = list(all_artworks_set)

            if available_artworks and num_ignores > 0:
                ignore_timestamps = generate_timestamps(
                    last_like_timestamp, num_ignores, 1, 96
                )
                selected_ignores = np.random.choice(
                    available_artworks,
                    size=min(num_ignores, len(available_artworks)),
                    replace=False,
                )

                # Generate multiple sets of ignores to increase the count
                for ts, art_id in zip(ignore_timestamps, selected_ignores):
                    # Add 1-2 ignore events for the same artwork
                    num_ignore_events = np.random.randint(1, 3)
                    for _ in range(num_ignore_events):
                        ignore_ts = (
                            ts - np.random.randint(1, 12) * 3600000
                        )  # Add some random hours difference
                        interactions.append(
                            {
                                "t_dat": ignore_ts,
                                "user_id": user_id,
                                "artwork_id": art_id,
                                "interaction_score": 0,
                                "prev_artwork_id": None,
                            }
                        )
                    user_artworks["ignored"].add(art_id)

            # Process likes and their clicks
            like_rows = user_likes.iter_rows(named=True)
            for row in like_rows:
                like_timestamp = row["t_dat"]
                artwork_id = row["artwork_id"]

                # Add clicks before like
                if np.random.random() < CLICK_BEFORE_PURCHASE_PROB:
                    num_pre_clicks = np.random.randint(1, 3)
                    for _ in range(num_pre_clicks):
                        click_timestamp = generate_timestamps(
                            like_timestamp, 1, 1, 48
                        )[0]
                        interactions.append(
                            {
                                "t_dat": click_timestamp,
                                "user_id": user_id,
                                "artwork_id": artwork_id,
                                "interaction_score": 1,
                                "prev_artwork_id": None,
                            }
                        )
                        user_artworks["clicked"].add(artwork_id)

                # Add like
                interactions.append(
                    {
                        "t_dat": like_timestamp,
                        "user_id": user_id,
                        "artwork_id": artwork_id,
                        "interaction_score": 2,
                        "prev_artwork_id": None,
                    }
                )
                user_artworks["liked"].add(artwork_id)

            # Generate extra clicks
            if np.random.random() < EXTRA_CLICKS_PROB:
                num_extra_clicks = np.random.randint(
                    MIN_EXTRA_CLICKS, MAX_EXTRA_CLICKS + 1
                )
                available_for_clicks = list(
                    all_artworks_set
                    - user_artworks["liked"]
                    - user_artworks["clicked"]
                    - user_artworks["ignored"]
                )

                if available_for_clicks and num_extra_clicks > 0:
                    click_timestamps = generate_timestamps(
                        last_like_timestamp, num_extra_clicks, 1, 72
                    )
                    selected_clicks = np.random.choice(
                        available_for_clicks,
                        size=min(num_extra_clicks, len(available_for_clicks)),
                        replace=False,
                    )

                    for ts, art_id in zip(click_timestamps, selected_clicks):
                        interactions.append(
                            {
                                "t_dat": ts,
                                "user_id": user_id,
                                "artwork_id": art_id,
                                "interaction_score": 1,
                                "prev_artwork_id": None,
                            }
                        )

    if not interactions:
        return pl.DataFrame(
            schema={
                "t_dat": pl.Int64,
                "user_id": pl.Utf8,
                "artwork_id": pl.Utf8,
                "interaction_score": pl.Int64,
                "prev_artwork_id": pl.Utf8,
            }
        )

    interaction_df = pl.DataFrame(interactions)
    sorted_df = interaction_df.sort(["user_id", "t_dat"])

    final_df = sorted_df.with_columns(
        [
            pl.col("artwork_id")
            .alias("prev_artwork_id")
            .shift(1)
            .over("user_id")
            .fill_null("START")
        ]
    )
    
    return final_df
