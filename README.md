# Art Recommendation System

# 📋 Prerequisites

## Local Tools
You'll need the following tools installed locally:
- [Python v3.11](https://www.python.org/downloads/)
- [uv v0.4.30](https://github.com/astral-sh/uv) - Python package installer and virtual environment manager
- [GNU Make 3.81](https://www.gnu.org/software/make/) - Build automation tool

# 🎯 Getting Started

## 1. Installation

Set up the project environment by running:
```bash
make install
```

This command will:
- Create a virtual environment using `uv`
- Activate the virtual environment
- Install all dependencies from `pyproject.toml`


# Project Report

## General description

The goal of the project is to develop a user interaction-based recommender system for artworks. This includes training multiple machine learning models (a Siamese network-like tower model and a ranking model) that can predict which artworks a user will like based on user data such as age, artistic preferences, lifestyle, and more. This data will be combined with artwork data, which includes:
- A short description
- The date
- The artist
- The medium it is painted on
- A broad category
Based on these sources, the models predict how likely it is that a user, with their profile and a list of previously liked artworks, will enjoy another given artwork.

First, the tower model provides a general ranking for each artwork. After filtering for duplicates, already liked artworks, and other criteria, the ranking model offers a fine-grained ranking to determine the order in which artworks should be displayed in the UI.

This is inspired by and based on [H&M Recommender System](https://github.com/decodingml/personalized-recommender-course).

## Technical description

Each string feature for user and artwork data is embedded using a pre-trained sentence transformer. These embeddings, along with categorical data and user ID embeddings, are used to generate an embedding for both the user and the artwork. The model responsible for this consists of multiple feed-forward dense layers with ReLU activation functions and normalization.

These two embeddings are trained to map into the same vector space, meaning that users who like an artwork will have similar embedding vectors. This is achieved using the TensorFlow Retrieval task with the Factorized TopK metric, a matrix factorization recommender model task. The user matrix and the artwork matrix are combined in a dot product to predict interaction scores between them (two similar embedding vectors will have a high dot product). The TopK approach compares the top K artworks for each user with the ground truth interactions from the dataset. This method is more accurate than a precision or recall metric since it ensures that relevance is considered in evaluating the recommender system (A. Sefidian, [Understanding Factorized TopK](https://iamirmasoud.com/2022/04/30/understanding-factorized-top-k-factorizedtopk-metric-for-recommendation-systems-with-example/#:~:text=The%20factorized%20top-k%20metric,previous%20interactions%20with%20the%20system)).

For both the dataset and the model, we use Hopsworks. The feature pipeline involves scaling, balancing the dataset features, and storing them in feature groups for the user, artworks, and transactions between users and artworks. These can then be combined into a feature view.

In the training pipeline, these features are retrieved, a model is trained, and the result is uploaded to a model registry. This model can then be downloaded and used for inference.

## Dataset

For our non-static dataset we used the [api](https://developers.artsy.net/) from [artsy](https://www.artsy.net/). This dataset includes many features for each artwork, such as a description, artist, date, and category. We enriched these features with a concise content description generated using an LLM, specifically OpenAI's API. An example prompt is: `Describe this image by color, mood, and aesthetic in no more than 4 lines of text`
However, we lacked user interaction data with artworks. To address this, we synthetically generated realistic user data using an LLM. We leveraged Artsy's feature of linking related artworks by categories, dates, artists, or descriptions.

First, we defined synthetic users by assigning them a random artwork. Based on this artwork, we selected three more from similar categories. These were then used as input to an LLM to generate user features consistent with the liked artworks. This approach ensured diverse user profiles (each user starts with a random artwork) while maintaining coherent interaction histories.

An example prompt to generate a user profile based on coherent artworks is as follows: `Here is a list of artworks that a users liked.\nComplete the user profile based on these images. \nAnswer with age (exact number), sex (F, M, N) and a creative sentence describing the user in general (culture, location, work, aestehtics, emotions...).\nFormat the response as a JSON object with the keys age, gender, and description.`.

The interaction dataset was created using these initial artworks. Further interactions are also generated when a "user" or "tester" clicks on more artworks in our UI. These interactions can then be used to refine the dataset further.


## UI
For the UI, we used Streamlit. The UI accesses the deployed Hopsworks query model and has defined user profiles. Within the interface, users can be selected, and artworks matching their profiles are recommended. These artworks can be clicked and liked, which refines the interaction data and improves future recommendations.

## Results

The deployed Streamlit app can be accessed [here](https://chinadupaya-art-recommendations-streamlit-app-7kiwzt.streamlit.app/).
Due to limitations with the free tier in Hopsworks, users cannot use the deployed model concurrently (only one user can use it a time). In such a case that this is encountered, click "Stop Deployments" and refresh the page to restart the deployments. This might need to be done a few times.

![UI Output](image.png)