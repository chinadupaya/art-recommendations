from datetime import datetime

import streamlit as st

from recsys.config import settings

from .feature_group_updater import get_fg_updater
from .interaction_tracker import get_tracker
from .utils import (
    fetch_and_process_image,
    get_item_image_url,
    print_header,
    process_description,
)



def display_item(item_id, score, artworks_fv, user_id, tracker, source):
    """Display a single item with its interactions"""
    image_url = get_item_image_url(item_id, artworks_fv)
    img = fetch_and_process_image(image_url)

    if img:
        st.image(img, use_column_width=True)
        st.write(f"**🎯 Score:** {score:.4f}")

        # View Details button
        details_key = f"{source}_details_{item_id}"
        if st.button("📝 View Details", key=details_key):
            tracker.track(user_id, item_id, "click")
            with st.expander("Item Details", expanded=True):
                description = process_description(
                    artworks_fv.get_feature_vector({"artwork_id": item_id})[-2]
                )
                st.write(description)

        # Buy button
        buy_key = f"{source}_buy_{item_id}"
        if st.button("🛒 Buy", key=buy_key):
            # Track interaction
            tracker.track(user_id, item_id, "like")

            # Insert transaction
            fg_updater = get_fg_updater()
            like_data = {"user_id": user_id, "artwork_id": item_id}

            if fg_updater.insert_transaction(like_data):
                st.success(f"✅ Item {item_id} liked!")
                st.experimental_rerun()
            else:
                st.error("Failed to record transaction, but like was tracked")


def user_recommendations(
    artworks_fv, ranking_deployment, query_model_deployment, user_id
):
    """Handle user-based recommendations"""
    tracker = get_tracker()

    # Initialize or update recommendations
    if "user_recs" not in st.session_state:
        st.session_state.user_recs = []
        st.session_state.prediction_time = None

    # Only get new predictions if:
    # 1. Button is clicked OR
    # 2. No recommendations exist OR
    # 3. User ID changed
    if (
        st.sidebar.button("Get Recommendations", key="get_recommendations_button")
        or not st.session_state.user_recs
        or "last_user_id" not in st.session_state
        or st.session_state.last_user_id != user_id
    ):
        with st.spinner("🔮 Getting recommendations..."):
            # Format timestamp with microseconds
            current_time = datetime.now()
            formatted_timestamp = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

            st.session_state.prediction_time = formatted_timestamp
            st.session_state.last_user_id = user_id

            # Get predictions from model
            # deployment_input = [
            #     {"user_id": user_id, "transaction_date": formatted_timestamp}
            # ]
            deployment_input = [
                {"user_id": user_id}
            ]

            # prediction = query_model_deployment.predict([{
            #     "signature_name": "serving_default",
            #     "instances": deployment_input
            # }])["predictions"]["ranking"]
            prediction = query_model_deployment.predict(inputs=deployment_input)[
                "predictions"
            ]["ranking"]

            # Filter out liked items
            available_items = [
                (item_id, score)
                for score, item_id in prediction
                if tracker.should_show_item(user_id, item_id)
            ]

            # Store recommendations and extras
            st.session_state.user_recs = available_items[:12]
            st.session_state.extra_recs = available_items[12:]

            # Track shown items
            tracker.track_shown_items(
                user_id,
                [(item_id, score) for item_id, score in st.session_state.user_recs],
            )

            st.sidebar.success("✅ Got new recommendations")

    # Display recommendations
    print_header("📝 Top 12 Recommendations:")

    if not st.session_state.user_recs:
        st.warning(
            "No recommendations available. Click 'Get Recommendations' to start."
        )
        return

    # Display items in 3x4 grid
    for row in range(3):
        cols = st.columns(4)
        for col in range(4):
            idx = row * 4 + col
            if idx < len(st.session_state.user_recs):
                item_id, score = st.session_state.user_recs[idx]
                if tracker.should_show_item(user_id, item_id):
                    with cols[col]:
                        display_item(
                            item_id,
                            score,
                            artworks_fv,
                            user_id,
                            tracker,
                            "user",
                        )
                else:
                    # Replace liked item with one from extras
                    if st.session_state.extra_recs:
                        new_item = st.session_state.extra_recs.pop(0)
                        st.session_state.user_recs.append(new_item)
                    st.session_state.user_recs.pop(idx)
                    st.experimental_rerun()



def get_fashion_recommendations(user_input, fashion_chain, gender):
    """Get recommendations from the LLM"""
    response = fashion_chain.run(user_input=user_input, gender=gender)
    items = response.strip().split(" | ")

    outfit_summary = items[-1] if len(items) > 1 else "No summary available."
    item_descriptions = items[:-1] if len(items) > 1 else items

    parsed_items = []
    for item in item_descriptions:
        try:
            emoji_category, description = item.split(" @ ", 1)
            emoji, category = emoji_category.split(" ", 1)
            parsed_items.append((emoji, category, description))
        except ValueError:
            parsed_items.append(("🔷", "Item", item))

    return parsed_items, outfit_summary



def display_category_items(emoji, category, items, artworks_fv, user_id, tracker):
    """Display items for a category and handle likes"""
    st.markdown(f"## {emoji} {category}")

    if items:
        st.write(f"**Recommendation: {items[0][0]}**")

        # Calculate number of rows needed
        items_per_row = 5
        num_rows = (len(items) + items_per_row - 1) // items_per_row

        need_rerun = False
        remaining_items = []

        # Display items row by row
        for row in range(num_rows):
            start_idx = row * items_per_row
            end_idx = min(start_idx + items_per_row, len(items))
            row_items = items[start_idx:end_idx]

            cols = st.columns(items_per_row)

            for idx, item_data in enumerate(row_items):
                if tracker.should_show_item(user_id, item_data[1][0]):
                    with cols[idx]:
                        remaining_items.append(item_data)

        st.markdown("---")
        return need_rerun, remaining_items
    return False, []


def get_similar_items(description, embedding_model, artworks_fv):
    """Get similar items based on description embedding"""
    description_embedding = embedding_model.encode(description)

    return artworks_fv.find_neighbors(description_embedding, k=25)
