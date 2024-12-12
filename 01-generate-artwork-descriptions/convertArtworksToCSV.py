import json
import csv

def convert_json_to_csv(json_file, csv_file):
    """
    Convert a JSON file of artworks to a CSV file.
    Extracts id, title, category, thumbnail link, and artists link.
    """
    try:
        # Load the JSON file
        with open(json_file, "r", encoding="utf-8") as f:
            artworks = json.load(f)
        
        # Open the CSV file for writing
        with open(csv_file, "w", encoding="utf-8", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            
            # Write header
            csvwriter.writerow(["id", "title", "category", "thumbnail_link", "artists_link", "genes_link", "similar_link"])
            
            # Write artwork data
            for artwork in artworks:
                art_id = artwork.get("id", "")
                title = artwork.get("title", "")
                category = artwork.get("category", "")
                thumbnail_link = artwork.get("_links", {}).get("thumbnail", {}).get("href", "")
                artists_link = artwork.get("_links", {}).get("artists", {}).get("href", "")
                genes_link = artwork.get("_links", {}).get("genes", {}).get("href", "")
                similar_link = artwork.get("_links", {}).get("similar_artworks", {}).get("href", "")
                # Write a row to the CSV
                csvwriter.writerow([art_id, title, category, thumbnail_link, artists_link, genes_link, similar_link])
        
        print(f"Successfully converted {json_file} to {csv_file}.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
if __name__ == "__main__":
    json_file = "artworks.json"  # Replace with your JSON file path
    csv_file = "artworks.csv"   # Output CSV file path
    convert_json_to_csv(json_file, csv_file)
