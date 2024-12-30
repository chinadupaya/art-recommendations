import logging
import os

import streamlit as st

# TO DO import recsys modules
from recsys.config import settings
from recsys.ui.feature_group_updater import get_fg_updater
from recsys.ui.interaction_tracker import get_tracker
from recsys.ui.recommenders import user_recommendations
from recsys.ui.utils import get_deployments

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
USER_IDS = [
    "a926fcb4-fcb9-461c-bcf3-94e99087488a",
    "3a0e200e-c233-49ce-bc70-e3ae2e782161",
    "cf8fc740-d851-490e-8dfb-6c853558ffeb",
    "152c7eb1-79d6-48b0-844d-c50f1ad5295c",
    "0be2e627-aacd-4945-b8ee-99162dc056af",
]

    

def initialize_services():
    """Initialize tracker, updater, and deployments"""
    tracker = get_tracker()
    fg_updater = get_fg_updater()

    logger.info("Initializing deployments...")
    with st.sidebar:
        with st.spinner("🚀 Starting Deployments..."):
           artworks_fv, ranking_deployment, query_model_deployment = get_deployments()
        st.success("✅ Deployments Ready")

        # Stop deployments button
        if st.button(
            "⏹️ Stop Deployments", key="stop_deployments_button", type="secondary"
        ):
            ranking_deployment.stop()
            query_model_deployment.stop()
            st.success("Deployments stopped successfully!")

    return tracker, fg_updater, artworks_fv, ranking_deployment, query_model_deployment

def show_interaction_dashboard(tracker, fg_updater):
    """Display interaction data and controls"""
    with st.sidebar.expander("📊 Interaction Dashboard", expanded=True):
        interaction_data = tracker.get_interactions_data()

        col1, col2, col3 = st.columns(3)
        total = len(interaction_data)
        clicks = len(interaction_data[interaction_data["interaction_score"] == 1])
        likes = len(interaction_data[interaction_data["interaction_score"] == 2])

        col1.metric("Total", total)
        col2.metric("Clicks", clicks)
        col3.metric("Likes", likes)

        st.dataframe(interaction_data, hide_index=True)
        fg_updater.process_interactions(tracker, force=True)


def process_pending_interactions(tracker, fg_updater):
    """Process interactions immediately"""
    fg_updater.process_interactions(tracker, force=True)



def main():
    # Initialize page
    """Initialize Streamlit page configuration"""
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")
    st.title("🎨 Art Recommendations")
    st.sidebar.title("⚙️ Configuration")

    # Initialize services
    tracker, fg_updater, articles_fv, ranking_deployment, query_model_deployment = (
        initialize_services()
    )

    # Select user
    user_id = st.sidebar.selectbox(
        "👤 Select User:", USER_IDS, key="selected_user"
    )

    # Process any pending interactions with notification
    # process_pending_interactions(tracker, fg_updater)

    # Interaction dashboard with OpenAI API key field
    # show_interaction_dashboard(tracker, fg_updater)

    # Handle page content
    # user_recommendations(
    #     articles_fv, ranking_deployment, query_model_deployment, user_id
    # )

if __name__ == "__main__":
    main()