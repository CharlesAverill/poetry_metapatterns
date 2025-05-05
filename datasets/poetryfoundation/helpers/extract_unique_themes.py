
"""
Script to extract all unique themes from the Poetry Foundation dataset CSV file
and write them to a new file.
"""
import csv
import os
import pandas as pd

def extract_unique_themes(input_csv_path, output_file_path):

    unique_themes = set()
    
    try:
        df = pd.read_csv(input_csv_path)
        
        # Process each tag value
        for tag_value in df['Tags'].dropna():
            if isinstance(tag_value, str):
                for delimiter in [',', ';', '|']:
                    if delimiter in tag_value:
                        tags = [t.strip() for t in tag_value.split(delimiter)]
                        for tag in tags:
                            if tag:  
                                unique_themes.add(tag)
                        break
                else:
                    
                    if tag_value.strip():
                        unique_themes.add(tag_value.strip())
    except Exception as e:
        print(f"Error processing CSV file: {e}")
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
    input_csv = os.path.join(os.path.dirname(__file__), "PoetryFoundationData_with_locations_and_years_filtered.csv")
    output_file = os.path.join(os.path.dirname(__file__), "unique_themes.txt")
    
    # Extract themes
    extract_unique_themes(input_csv, output_file)
