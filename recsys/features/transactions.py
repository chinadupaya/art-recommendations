import numpy as np
import pandas as pd
import polars as pl
from hopsworks import udf
from datetime import datetime


def compute_features_transactions(df: pl.DataFrame) -> pl.DataFrame:
    required_columns = ["transaction_id", "user_id", "artwork_id", "t_dat"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Columns {', '.join(missing_columns)} not found in the DataFrame"
        )
    return (
        df.with_columns(
            [
                pl.col("t_dat").dt.year().alias("year"),
                pl.col("t_dat").dt.month().alias("month"),
                pl.col("t_dat").dt.day().alias("day"),
                pl.col("t_dat").dt.weekday().alias("day_of_week"),
            ]
        )
        .with_columns([(pl.col("t_dat").cast(pl.Int64) // 1_000_000).alias("t_dat")])
    )

