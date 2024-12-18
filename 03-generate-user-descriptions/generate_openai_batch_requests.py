import pandas as pd
import json
from urllib.parse import urlparse
from tqdm import tqdm


def is_valid_url(url):
    """Check if a URL is valid without calling it."""
    if type(url) is float:
        return False
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])


# Load the CSV file into a DataFrame
file_path = '../data/transaction-data.csv'
transaction_data = pd.read_csv(file_path)

# Group the data by user_id
grouped_data = transaction_data.groupby('user_id')
json_list = []

# Iterate through each group
for user_id, group in tqdm(grouped_data,total=len(grouped_data)):
    # Get the first transaction for the user
    first_transaction = group.iloc[0]

    images = [{"type": "text", "text": """Here is a list of artworks that a users liked.
Complete the user profile based on these images. 
Answer with exact age, sex (F or M) and a creative description of the user (culture, location, aestehtics, emotions...).
Format the response as a JSON object with the keys age, gender, and description."""}]

    thumb_count = 0
    for url in group["thumbnail_link"]:
        if is_valid_url(url) and thumb_count < 3:
            images.append({"type": "image_url", "image_url": {"url": url}})
            thumb_count += 1

    # Create the JSON object
    json_obj = {
        "custom_id": first_transaction['user_id'],
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a psychologist and an art critic. Be concise and creative."},
                {"role": "user", "content": images}
            ],
            "max_tokens": 300
        }
    }
    
    # Add the JSON object to the list
    json_list.append(json_obj)

# Convert the list of JSON objects to a JSON string
json_output = json.dumps(json_list, indent=4)

# Write the JSON output to a JSONL file
output_file_path = 'user_batch_0-10_000.jsonl'
with open(output_file_path, 'w') as output_file:
    for json_obj in json_list:
        output_file.write(json.dumps(json_obj) + '\n')


