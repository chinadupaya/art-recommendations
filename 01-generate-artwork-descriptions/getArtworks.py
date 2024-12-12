import requests
import time
import os

# Constants
API_BASE_URL = "https://api.artsy.net/api"
CLIENT_ID = os.environ.get('CLIENT_ID') # Replace with your Artsy client_id
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')  # Replace with your Artsy client_secret
RATE_LIMIT = 5  # 5 requests per second
ARTWORKS_COUNT = 27577
def get_access_token():
    """
    Fetch the access token from the Artsy API.
    """
    auth_url = f"{API_BASE_URL}/tokens/xapp_token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(auth_url, json=payload)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()["token"]

def get_access_token():
    """
    Fetch the access token from the Artsy API.
    """
    auth_url = f"{API_BASE_URL}/tokens/xapp_token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(auth_url, json=payload)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()["token"]


def fetch_artworks(token):
    """
    Fetch all artworks using the Artsy API.
    """
    artworks = []
    headers = {
        "X-Xapp-Token": token,
    }
    next_page_url = f"{API_BASE_URL}/artworks?page=1&size=50"
    counter = 0
    while next_page_url:
        print (str((counter / ARTWORKS_COUNT) * 100) + "% completed")
        response = requests.get(next_page_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        artworks.extend(data["_embedded"]["artworks"])
        next_page_url = data.get("_links", {}).get("next", {}).get("href", None)
        # Respect rate limiting
        time.sleep(1 / RATE_LIMIT)
        counter += 50
    
    return artworks

def save_artworks_to_file(artworks, filename="artworks.json"):
    """
    Save artworks data to a file in JSON format.
    """
    import json
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(artworks, f, ensure_ascii=False, indent=4)

def main():
    """
    Main function to download all artworks from Artsy API.
    """
    try:
        print("Authenticating...")
        token = get_access_token()
        # token = get_access_token()
        print("Fetching artworks...")
        artworks = fetch_artworks(token)
        print(f"Fetched {len(artworks)} artworks.")
        save_artworks_to_file(artworks)
        print("Artworks saved to artworks.json")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
