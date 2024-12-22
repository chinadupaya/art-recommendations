import random

import polars as pl
from loguru import logger

from recsys.config import UserDatasetSize


class DatasetSampler:
    _SIZES = {
        UserDatasetSize.LARGE: 50_000,
        UserDatasetSize.MEDIUM: 5_000,
        UserDatasetSize.SMALL: 1_000,
    }

    def __init__(self, size: UserDatasetSize) -> None:
        self._size = size

    @classmethod
    def get_supported_sizes(cls) -> dict:
        return cls._SIZES

    def sample(
        self, users_df: pl.DataFrame, transations_df: pl.DataFrame
    ) -> dict[str, pl.DataFrame]:
        random.seed(27)

        n_users = self._SIZES[self._size]
        logger.info(f"Sampling {n_users} users.")
        users_df = users_df.sample(n=n_users)

        logger.info(
            f"Number of transactions for all the users: {transations_df.height}"
        )
        transations_df = transations_df.join(
            users_df.select("user_id"), on="user_id"
        )
        logger.info(
            f"Number of transactions for the {n_users} sampled users: {transations_df.height}"
        )

        return {"users": users_df, "transactions": transations_df}
    
def drop_na_age(df: pl.DataFrame) -> pl.DataFrame:
    """
    Drop rows with null values in the 'age' column.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing the 'age' column.

    Returns:
    - pl.DataFrame: DataFrame with rows containing null 'age' values removed.
    """
    return df.drop_nulls(subset=["age"])

def create_age_group() -> pl.Expr:
    """
    Create an expression to categorize age into groups.

    Returns:
    - pl.Expr: Polars expression that categorizes 'age' into predefined age groups.
    """
    return (
        pl.when(pl.col("age").is_between(0, 18))
        .then(pl.lit("0-18"))
        .when(pl.col("age").is_between(19, 25))
        .then(pl.lit("19-25"))
        .when(pl.col("age").is_between(26, 35))
        .then(pl.lit("26-35"))
        .when(pl.col("age").is_between(36, 45))
        .then(pl.lit("36-45"))
        .when(pl.col("age").is_between(46, 55))
        .then(pl.lit("46-55"))
        .when(pl.col("age").is_between(56, 65))
        .then(pl.lit("56-65"))
        .otherwise(pl.lit("66+"))
    ).alias("age_group")




def compute_features_users(
    df: pl.DataFrame, drop_null_age: bool = False
) -> pl.DataFrame:
    required_columns = ["user_id", "age", "preference", "gender"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Columns {', '.join(missing_columns)} not found in the DataFrame"
        )
    df = (
        df.pipe(drop_na_age)
        .with_columns([create_age_group(), pl.col("age").cast(pl.Float64)])
    )

    if drop_null_age is True:
        df = df.drop_nulls(subset=["age"])

    return df

