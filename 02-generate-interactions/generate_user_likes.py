import csv
import random
import time
import requests
import os
import uuid

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


def get_artwork_data(token, similar_link):
    """
    Fetches data from the Artsy API using the provided `similar_link`.

    Args:
        similar_link (str): The URL for the API request.

    Returns:
        list: A list of artwork IDs returned by the API.
    """
    try:
        headers = {
            "X-Xapp-Token": token  # Replace with your Artsy API token
        }
        response = requests.get(similar_link, headers=headers)
        response.raise_for_status()
        data = response.json()

       # Extract artwork IDs and thumbnail links from the response
        artworks = [
            {
                "id": artwork.get("id"),
                "thumbnail_link": artwork.get("_links", {}).get("thumbnail", {}).get("href")
            }
            for artwork in data.get("_embedded", {}).get("artworks", [])
        ]
        return artworks

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {similar_link}: {e}")
        return []

def generate_transaction_data(token, input_csv, output_csv):
    """
    Generate a CSV file with transaction data including:
    - Random transaction_id
    - User ID
    - Artwork ID
    - Thumbnail Link

    Args:
        input_csv (str): Path to the input CSV file (user-artworks.csv).
        output_csv (str): Path to the output CSV file.
    """
    used_transaction_ids = set()
    try:
        with open(input_csv, "r", encoding="utf-8") as infile, open(output_csv, "w", encoding="utf-8", newline="") as outfile:
            reader = csv.DictReader(infile)
            fieldnames = ["transaction_id", "user_id", "artwork_id", "thumbnail_link"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            counter = 0
            for row in reader:
                user_id = row.get("id")
                similar_link = row.get("similar_link")
                r_artwork_id = row.get("artwork_id")
                r_thumbnail_link= row.get("thumbnail_link")

                if not similar_link:
                    continue
                writer.writerow({
                    "transaction_id": uuid.uuid4(),
                    "user_id": user_id,
                    "artwork_id": r_artwork_id,
                    "thumbnail_link": r_thumbnail_link,
                })
                # Fetch artwork data from the API
                artworks = get_artwork_data(token, similar_link)
                
                # Rate limit: Wait to comply with the API's limit of 5 requests per second
                time.sleep(0.2)  # 200ms pause between requests

                # Create a row for each artwork
                for artwork in artworks:
                    writer.writerow({
                        "transaction_id": uuid.uuid4(),
                        "user_id": user_id,
                        "artwork_id": artwork["id"],
                        "thumbnail_link": artwork["thumbnail_link"]
                    })
                print(str((counter / 54000) * 100) + "% done")
                counter+=1

        print(f"Transaction data written to {output_csv}.")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    try:
        print("Authenticating...")
        token = get_access_token()
        print("Fetching artworks...") 
        input_csv = "user-artworks.csv"  # Path to the input CSV file
        output_csv = "transaction-data.csv"  # Path to the output CSV file
        generate_transaction_data(token, input_csv, output_csv)
        print("Artworks saved to artworks.json")
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
if __name__ == "__main__":
   main()
