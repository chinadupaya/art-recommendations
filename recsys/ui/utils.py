import re
from io import BytesIO

import requests
import streamlit as st
from PIL import Image, UnidentifiedImageError

from recsys import hopsworks_integration


def print_header(text, font_size=22):
    res = f'<span style="font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True)

@st.cache_data()
def fetch_and_process_image(image_url, width=200, height=300):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((width, height), Image.LANCZOS)
        return img
    except (UnidentifiedImageError, requests.RequestException, IOError):
        return None


def process_description(description):
    return description if description else "No details available"
    # details_match = re.search(r"Details: (.+?)(?:\n|$)", description)
    # return details_match.group(1) if details_match else "No details available."


def get_item_image_url(item_id, artworks_fv):
    # return index of image
    return artworks_fv.get_feature_vector({"artwork_id": item_id})[3]



@st.cache_resource()
def get_deployments():
    project, fs = hopsworks_integration.get_feature_store()

    ms = project.get_model_serving()

    artworks_fv = fs.get_feature_view(
        name="artworks",
        version=1,
    )

    query_model_deployment = ms.get_deployment(
        hopsworks_integration.two_tower_serving.HopsworksQueryModel.deployment_name
    )
    ranking_deployment = ms.get_deployment(
        hopsworks_integration.ranking_serving.HopsworksRankingModel.deployment_name
    )

    ranking_deployment.start(await_running=180)
    query_model_deployment.start(await_running=180)

    return artworks_fv, ranking_deployment, query_model_deployment