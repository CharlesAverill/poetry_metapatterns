"""
Script to extract all unique themes (tags) from the DLK dataset CSV file
and write them to a new file.
"""

import csv
import os

def extract_unique_themes(input_csv_path, output_file_path):

    unique_themes = set()
    
    # Read the CSV file
    try:
        with open(input_csv_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            header = next(csv_reader)
            
            # Process each row
            for row in csv_reader:
                if len(row) >= 7: 
                    tag = row[6].strip()
                    if tag:  
                        unique_themes.add(tag)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False
    
    # Write unique themes to the output file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            # Sort themes alphabetically
            sorted_themes = sorted(unique_themes)
            
            # Write each theme on a new line
            for theme in sorted_themes:
                output_file.write(f"{theme}\n")
                
            print(f"Successfully extracted {len(sorted_themes)} unique themes to {output_file_path}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Define input and output paths
    input_csv = os.path.join(os.path.dirname(__file__), "DLK", "dlk_poems.csv")
    output_file = os.path.join(os.path.dirname(__file__), "DLK", "unique_themes.txt")
    
    # Extract themes
    extract_unique_themes(input_csv, output_file)
