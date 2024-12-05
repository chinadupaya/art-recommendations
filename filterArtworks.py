import csv

def filter_csv(input_csv, output_csv):
    """
    Filters a CSV file based on specified conditions:
    - Category is one of Painting, Photography, Posters, Print, or Textile Arts.
    - Non-null thumbnail_link and artists_link.
    """
    valid_categories = {"Painting", "Photography", "Posters", "Print", "Textile Arts"}
    
    try:
        # Open the input CSV for reading
        with open(input_csv, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            
            # Open the output CSV for writing
            with open(output_csv, "w", encoding="utf-8", newline="") as outfile:
                fieldnames = reader.fieldnames  # Preserve the same header as the input
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                
                # Write the header row
                writer.writeheader()
                
                # Write only rows that match the criteria
                for row in reader:
                    category = row.get("category", "")
                    thumbnail_link = row.get("thumbnail_link", "").strip()
                    artists_link = row.get("artists_link", "").strip()
                    genes_link = row.get("genes_link", "").strip()
                    
                    if (
                        category in valid_categories
                        and thumbnail_link  # Ensure not empty
                        and artists_link    # Ensure not empty
                        and genes_link    # Ensure not empty
                    ):
                        writer.writerow(row)
        
        print(f"Filtered data saved to {output_csv}.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
if __name__ == "__main__":
    input_csv = "artworks.csv"  # Replace with the input CSV file path
    output_csv = "filtered_artworks.csv"  # Replace with the output CSV file path
    filter_csv(input_csv, output_csv)
