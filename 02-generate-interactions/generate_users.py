import csv
import random
import uuid

def generate_user_artworks(input_csv, output_csv, num_ids=54000):
    """
    Generates a new CSV file with 54,000 random user IDs and maps them
    to random artwork IDs from the filtered_artworks.csv.
    """
    try:
         # Read the artwork IDs and similar links from the input CSV
        artwork_data = []
        with open(input_csv, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                artwork_id = row.get("id", "").strip()
                similar_link = row.get("similar_link", "").strip()
                thumbnail_link = row.get("thumbnail_link", "").strip()
                if artwork_id and similar_link and thumbnail_link:  # Only include rows with non-empty artwork_id and similar_link
                    artwork_data.append({"artwork_id": artwork_id, "similar_link": similar_link, "thumbnail_link": thumbnail_link})
        
        if not artwork_data:
            raise ValueError("No valid artwork data found in the input CSV.")
        
        # Generate random user IDs
        user_artworks = []
        for _ in range(num_ids):
            random_artwork = random.choice(artwork_data)     # Pick a random artwork entry
            user_artworks.append({
                "id": uuid.uuid4(),
                "artwork_id": random_artwork["artwork_id"],
                "similar_link": random_artwork["similar_link"],
                "thumbnail_link": random_artwork["thumbnail_link"]
            })

        # Write the data to the output CSV
        with open(output_csv, "w", encoding="utf-8", newline="") as outfile:
            fieldnames = ["id", "artwork_id", "similar_link", "thumbnail_link"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(user_artworks)
        
        print(f"Generated {num_ids} rows in {output_csv}.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
if __name__ == "__main__":
    input_csv = "filtered_artworks.csv"  # Path to the input CSV file
    output_csv = "user-artworks.csv"    # Path to the output CSV file
    generate_user_artworks(input_csv, output_csv)
