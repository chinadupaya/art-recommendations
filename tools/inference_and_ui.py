import logging
import os

import streamlit as st

# TO DO import recsys modules

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_page():
    """Initialize Streamlit page configuration"""
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")
    st.title("🎨 Art Recommendations")
    st.sidebar.title("⚙️ Configuration")


def main():
    # Initialize page
    initialize_page()

    # TO DO: Initialize services

    # Page selection
    page_options = ["Customer Recommendations"]
    page_selection = st.sidebar.radio("📑 Choose Page:", page_options)
    

