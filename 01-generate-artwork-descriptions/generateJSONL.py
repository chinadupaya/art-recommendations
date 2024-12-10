import csv
import json

def generate_openai_batch_jsonl(input_csv, output_jsonl):
    """
    Generate a .jsonl file suitable for OpenAI's Batch API from a filtered CSV.
    Each JSON object represents a prompt to describe an image by color, mood, and aesthetic.
    """
    try:
        with open(input_csv, "r", encoding="utf-8") as infile, open(output_jsonl, "w", encoding="utf-8") as outfile:
            reader = csv.DictReader(infile)
            
            for row in reader:
                id = row.get("id", "").strip()
                thumbnail_link = row.get("thumbnail_link", "").strip()
                if thumbnail_link:  # Ensure the thumbnail link is not empty
                    # Create the JSON object for OpenAI's Batch API
                    request = {
                        "custom_id": id,
                        "method": "POST",
                        "url": "/v1/chat/completions",
                        "body": {
                            "model": "gpt-4",  # Specify the OpenAI model
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are an expert art critic and designer."
                                },
                                {
                                    "role": "user",
                                    "content": f"Describe the image in this link by color, mood, and aesthetic: {thumbnail_link}"
                                }
                            ],
                            "max_tokens": 1000
                        }
                    }
                    # Write the JSON object as a line in the .jsonl file
                    outfile.write(json.dumps(request) + "\n")
        
        print(f"OpenAI-compatible JSONL file created successfully at {output_jsonl}.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
if __name__ == "__main__":
    input_csv = "filtered_artworks.csv"  # Replace with your filtered CSV file path
    output_jsonl = "openai_batch_requests.jsonl"  # Output JSONL file path
    generate_openai_batch_jsonl(input_csv, output_jsonl)
