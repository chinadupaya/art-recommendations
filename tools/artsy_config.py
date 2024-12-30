import requests
import os


# Constants
CLIENT_ID = os.environ.get('CLIENT_ID') # Replace with your Artsy client_id
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')  # Replace with your Artsy client_secret

def get_access_token():
    """
    Fetch the access token from the Artsy API.
    """
    try:
        auth_url = "https://api.artsy.net/api/tokens/xapp_token"
        response = requests.post(auth_url, data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        })
        response.raise_for_status()  # Raise an error for bad status codes
        token = response.json().get("token")
        if not token:
            raise ValueError("Token not found in the response.")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching token: {e}")
        raise
