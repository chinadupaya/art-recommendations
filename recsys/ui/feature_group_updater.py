import logging
import math
import random
from datetime import datetime

from recsys.config import settings

import hopsworks
import pandas as pd
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureGroupUpdater:
    def __init__(self):
        """Initialize the FeatureGroup updater"""
        self._initialize_feature_groups()

    def _initialize_feature_groups(self) -> None:
        """Initialize connection to Hopsworks Feature Groups"""
        try:
            if "feature_group" not in st.session_state:
                logger.info("📡 Initializing Hopsworks Feature Groups connection...")
                # project = hopsworks.login(api_key_value="H")
                # fs = project.get_feature_store(name='id2223artsy_featurestore')
                project = hopsworks.login()
                fs = project.get_feature_store(name='id2223artsy_featurestore')

                # Initialize interactions feature group
                st.session_state.feature_group = fs.get_feature_group(
                    "interactions",
                    version=1,
                )

                # Initialize transactions feature group
                st.session_state.transactions_fg = fs.get_feature_group(
                    "transactions",
                    version=1,
                )
                logger.info("✅ Feature Groups connection established")

        except Exception as e:
            logger.error(f"Failed to initialize Feature Groups connection: {str(e)}")
            st.error(
                "❌ Failed to connect to Feature Groups. Check terminal for details."
            )
            raise

    def _prepare_transaction_for_insertion(self, like_data: dict) -> pd.DataFrame:
        """Prepare transaction data for insertion into transactions feature group"""
        try:
            timestamp = datetime.now()

            transaction = {
                "t_dat": int(timestamp.timestamp()),
                "user_id": str(like_data["user_id"]),
                "artwork_id": str(like_data["artwork_id"]),
                "thumbnail_link":  str(like_data["thumbnail_link"]),
                "year": timestamp.year,
                "month": timestamp.month,
                "day": timestamp.day,
                "day_of_week": timestamp.weekday(),
            }

            df = pd.DataFrame([transaction])

            # Ensure correct data types
            df["t_dat"] = df["t_dat"].astype("int64")
            df["user_id"] = df["user_id"].astype(str)
            df["artwork_id"] = df["artwork_id"].astype(str)
            df["thumbnail_link"] = df["thumbnail_link"].astype("str")
            df["sales_channel_id"] = df["sales_channel_id"].astype("int64")
            df["year"] = df["year"].astype("int32")
            df["month"] = df["month"].astype("int32")
            df["day"] = df["day"].astype("int32")
            df["day_of_week"] = df["day_of_week"].astype("int32")

            logger.info(f"Prepared transaction for insertion: {transaction}")
            return df

        except Exception as e:
            logger.error(f"Error preparing transaction data: {str(e)}")
            return None

    def insert_transaction(self, like_data: dict) -> bool:
        """Insert a single transaction into transactions feature group"""
        try:
            transaction_df = self._prepare_transaction_for_insertion(like_data)

            if transaction_df is not None:
                logger.info("Inserting transaction...")
                with st.spinner("💫 Recording transaction..."):
                    st.session_state.transactions_fg.multi_part_insert(transaction_df)
                logger.info("✅ Transaction inserted successfully")
                return True

        except Exception as e:
            logger.error(f"Failed to insert transaction: {str(e)}")
            st.error("❌ Failed to insert transaction. Check terminal for details.")

        return False

    def _prepare_interactions_for_insertion(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare interactions dataframe for insertion"""
        if df is None or df.empty:
            return None

        try:
            # Convert timestamp to Unix timestamp if needed
            if not pd.api.types.is_integer_dtype(df["t_dat"]):
                df["t_dat"] = pd.to_datetime(df["t_dat"]).astype("int64") // 10**9

            prepared_df = pd.DataFrame(
                {
                    "t_dat": df["t_dat"].astype("int64"),
                    "user_id": df["user_id"].astype(str),
                    "artwork_id": df["artwork_id"].astype(str),
                    "interaction_score": df["interaction_score"].astype("int64"),
                    "prev_artwork_id": df["prev_artwork_id"].astype(str),
                }
            )

            logger.info("Prepared interaction for insertion")
            return prepared_df

        except Exception as e:
            logger.error(f"Error preparing interaction data: {str(e)}")
            return None

    def process_interactions(self, tracker, force: bool = False) -> bool:
        """Process and insert interactions immediately"""
        try:
            interactions_df = tracker.get_interactions_data()

            if interactions_df.empty:
                return False

            prepared_df = self._prepare_interactions_for_insertion(interactions_df)
            if prepared_df is not None:
                logger.info("Inserting interactions...")
                st.session_state.feature_group.multi_part_insert(prepared_df)
                logger.info("✅ Interactions inserted successfully")
                return True

        except Exception as e:
            logger.error(f"Error processing interactions: {str(e)}")
            return False

        return False


def get_fg_updater():
    """Get or create FeatureGroupUpdater instance"""
    if "fg_updater" not in st.session_state:
        st.session_state.fg_updater = FeatureGroupUpdater()
    return st.session_state.fg_updater
