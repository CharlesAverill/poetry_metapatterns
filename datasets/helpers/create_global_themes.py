#!/usr/bin/env python3
"""
Script to create a unified global theme set by combining and consolidating
themes from both DLK and Poetry Foundation datasets.
"""

import csv
import os
import re
from collections import defaultdict

# Define the mapping from both source theme sets to global themes
GLOBAL_THEME_MAPPING = {
    # Nature & Environment
    "Nature": "Nature & Environment",
    "& Streams": "Nature & Environment",
    "Animals": "Nature & Environment",
    "Rivers": "Nature & Environment", 
    "Seas": "Nature & Environment",
    "Trees & Flowers": "Nature & Environment",
    "Weather": "Nature & Environment",
    "Planets": "Nature & Environment",
    "Heavens": "Nature & Environment",
    "Stars": "Nature & Environment",
    "Landscapes & Pastorals": "Nature & Environment",
    
    # Life & Living
    "Life": "Life & Living",
    "Living": "Life & Living",
    "Life Choices": "Life & Living",
    "Human Experience": "Life & Living",
    "Coming of Age": "Life & Living",
    "Growing Old": "Life & Living",
    "Youth": "Youth & Coming of Age",
    
    # Love & Relationships
    "Love": "Love & Relationships",
    "Relationships": "Love & Relationships",
    "Break-ups & Vexed Love": "Love & Relationships",
    "Men & Women": "Love & Relationships",
    "Friendship": "Love & Relationships",
    "Separation & Divorce": "Love & Relationships",
    "Desire": "Love & Relationships",
    
    # Death & Loss
    "Death": "Death & Loss",
    "Heartache & Loss": "Death & Loss",
    "Sorrow & Grieving": "Death & Loss",
    "Sorrow": "Death & Loss",
    
    # Time & Temporality
    "Time": "Time & Temporality",
    "Time & Brevity": "Time & Temporality",
    
    # Religion & Spirituality
    "Religion": "Religion & Spirituality",
    "God & the Divine": "Religion & Spirituality",
    "Faith & Doubt": "Religion & Spirituality",
    "The Spiritual": "Religion & Spirituality",
    
    # Society & Politics
    "Society": "Society & Politics",
    "History & Politics": "Society & Politics",
    "Social Commentaries": "Society & Politics",
    "Class": "Society & Politics",
    "Race & Ethnicity": "Society & Politics",
    "Money & Economics": "Society & Politics",
    "Crime & Punishment": "Society & Politics",
    
    # War & Conflict
    "War": "War & Conflict",
    "War & Conflict": "War & Conflict",
    
    # Arts & Culture
    "Art": "Arts & Culture",
    "Arts & Sciences": "Arts & Culture",
    "Music": "Arts & Culture",
    "Poetry & Poets": "Arts & Culture",
    "Language & Linguistics": "Arts & Culture",
    "Reading & Books": "Arts & Culture",
    "Photography & Film": "Arts & Culture",
    "Popular Culture": "Arts & Culture",
    
    # Mind & Emotions
    "Self": "Mind & Emotions",
    "The Mind": "Mind & Emotions",
    "Joy": "Mind & Emotions",
    "Fear": "Mind & Emotions",
    "Hope": "Mind & Emotions",
    "Solitude": "Mind & Emotions",
    "Existentialism": "Mind & Emotions",
    "Acceptance": "Mind & Emotions",
    
    # Body & Health
    "The Body": "Body & Health",
    "Health & Illness": "Body & Health",
    
    # Wisdom & Knowledge
    "Wisdom": "Wisdom & Knowledge",
    "School & Learning": "Wisdom & Knowledge",
    "Sciences": "Wisdom & Knowledge",
    
    # Morality & Ethics
    "Virtue": "Morality & Ethics",
    "Vice": "Morality & Ethics",
    
    # Family & Home
    "Family & Ancestors": "Family & Home",
    "Home Life": "Family & Home",
    "Parenthood": "Family & Home",
    "Pets": "Family & Home",
    
    # Activities & Work
    "Activities": "Activities & Work",
    "Jobs & Working": "Activities & Work",
    "Eating & Drinking": "Activities & Work",
    "Travels & Journeys": "Activities & Work",
    
    # Identity & Self
    "Gay": "Identity & Self",
    "Lesbian": "Identity & Self",
    "Queer": "Identity & Self",
    
    # Other categories
    "Birth & Birthdays": "Life Cycles",
    "Fall": "Seasons",
    "Power": "Power & Freedom",
    "Freedom": "Power & Freedom",
    "Fate": "Fate & Destiny",
    "Cities & Urban Life": "Places & Spaces",
    "Humor & Satire": "Humor & Play",
    "Disappointment & Failure": "Challenge & Adversity",
    "Realistic & Complicated": "Complexity & Paradox",
    
    # Map Miscellaneous as default category
    "Miscellaneous": "Miscellaneous"
}

# Ensure all DLK themes are mapped
DLK_THEMES = [
    "Acceptance", "Art", "Death", "Existentialism", "Fate", "Fear", "Freedom", "Friendship", 
    "Hope", "Human Experience", "Joy", "Life", "Love", "Miscellaneous", "Nature", "Power", 
    "Religion", "Self", "Society", "Solitude", "Sorrow", "Time", "Vice", "Virtue", "War", 
    "Wisdom", "Youth"
]

# Ensure all Poetry Foundation themes are mapped
PF_THEMES = [
    "& Streams", "Activities", "Animals", "Arts & Sciences", "Birth & Birthdays", "Break-ups & Vexed Love",
    "Cities & Urban Life", "Class", "Coming of Age", "Crime & Punishment", "Death", "Desire",
    "Disappointment & Failure", "Eating & Drinking", "Faith & Doubt", "Fall", "Family & Ancestors",
    "Gay", "God & the Divine", "Growing Old", "Health & Illness", "Heartache & Loss", "Heavens",
    "History & Politics", "Home Life", "Humor & Satire", "Jobs & Working", "Landscapes & Pastorals",
    "Language & Linguistics", "Lesbian", "Life Choices", "Living", "Love", "Men & Women",
    "Money & Economics", "Music", "Nature", "Parenthood", "Pets", "Photography & Film", "Planets",
    "Poetry & Poets", "Popular Culture", "Queer", "Race & Ethnicity", "Reading & Books",
    "Realistic & Complicated", "Relationships", "Rivers", "School & Learning", "Sciences", "Seas",
    "Separation & Divorce", "Social Commentaries", "Sorrow & Grieving", "Stars", "The Body",
    "The Mind", "The Spiritual", "Time & Brevity", "Travels & Journeys", "Trees & Flowers",
    "War & Conflict", "Weather", "Youth"
]

def get_all_global_themes():
    """Get the unified set of global themes."""
    # Extract all unique values in the mapping
    global_themes = set(GLOBAL_THEME_MAPPING.values())
    return sorted(list(global_themes))

def verify_all_themes_mapped():
    """Verify that all themes from both datasets are mapped to global themes."""
    unmapped_dlk = [theme for theme in DLK_THEMES if theme not in GLOBAL_THEME_MAPPING]
    unmapped_pf = [theme for theme in PF_THEMES if theme not in GLOBAL_THEME_MAPPING]
    
    if unmapped_dlk:
        print(f"Warning: These DLK themes are not mapped: {unmapped_dlk}")
        
    if unmapped_pf:
        print(f"Warning: These Poetry Foundation themes are not mapped: {unmapped_pf}")
        
    return not (unmapped_dlk or unmapped_pf)

def save_global_themes(output_path):
    """Save the global theme set to a file."""
    global_themes = get_all_global_themes()
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for theme in global_themes:
                f.write(f"{theme}\n")
            
        print(f"Successfully saved {len(global_themes)} global themes to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving global themes: {e}")
        return False

def update_dlk_dataset(input_csv_path, output_csv_path):
    """Update the DLK dataset with global themes."""
    try:
        with open(input_csv_path, 'r', encoding='utf-8') as input_file, \
             open(output_csv_path, 'w', encoding='utf-8', newline='') as output_file:
            
            csv_reader = csv.reader(input_file)
            csv_writer = csv.writer(output_file)
            
            # Get header
            header = next(csv_reader)
            csv_writer.writerow(header)
            
            # Process each row
            for row in csv_reader:
                if len(row) >= 7:  # Assuming tag is the 7th column (index 6)
                    original_tag = row[6].strip()
                    if original_tag and original_tag in GLOBAL_THEME_MAPPING:
                        row[6] = GLOBAL_THEME_MAPPING[original_tag]
                    elif original_tag:
                        # If tag is not directly mapped, try to find a partial match
                        matched = False
                        for dlk_theme in DLK_THEMES:
                            if dlk_theme in original_tag:
                                row[6] = GLOBAL_THEME_MAPPING[dlk_theme]
                                matched = True
                                break
                        
                        if not matched:
                            row[6] = "Miscellaneous"
                
                csv_writer.writerow(row)
                
        print(f"Successfully updated DLK dataset and saved to {output_csv_path}")
        return True
    except Exception as e:
        print(f"Error updating DLK dataset: {e}")
        return False

def update_pf_dataset(input_csv_path, output_csv_path):
    """Update the Poetry Foundation dataset with global themes."""
    try:
        with open(input_csv_path, 'r', encoding='utf-8') as input_file, \
             open(output_csv_path, 'w', encoding='utf-8', newline='') as output_file:
            
            csv_reader = csv.reader(input_file)
            csv_writer = csv.writer(output_file)
            
            # Get header
            header = next(csv_reader)
            tag_index = header.index('Tags') if 'Tags' in header else None
            
            if tag_index is None:
                print("Error: 'Tags' column not found in Poetry Foundation dataset")
                return False
                
            csv_writer.writerow(header)
            
            # Process each row
            for row in csv_reader:
                if len(row) > tag_index:
                    tags = row[tag_index].split(',')
                    updated_tags = []
                    
                    for tag in tags:
                        tag = tag.strip()
                        if tag in GLOBAL_THEME_MAPPING:
                            updated_tags.append(GLOBAL_THEME_MAPPING[tag])
                        else:
                            # If tag is not directly mapped, try to find a partial match
                            matched = False
                            for pf_theme in PF_THEMES:
                                if tag == pf_theme or pf_theme in tag:
                                    updated_tags.append(GLOBAL_THEME_MAPPING[pf_theme])
                                    matched = True
                                    break
                            
                            if not matched:
                                updated_tags.append("Miscellaneous")
                    
                    row[tag_index] = ','.join(updated_tags)
                
                csv_writer.writerow(row)
                
        print(f"Successfully updated Poetry Foundation dataset and saved to {output_csv_path}")
        return True
    except Exception as e:
        print(f"Error updating Poetry Foundation dataset: {e}")
        return False

def find_pf_csv():
    """Find the Poetry Foundation CSV file."""
    pf_dir = os.path.join(os.path.dirname(__file__), "poetryfoundation")
    for file in os.listdir(pf_dir):
        if file.endswith('.csv'):
            return os.path.join(pf_dir, file)
    return None

if __name__ == "__main__":
    # Define paths
    base_dir = os.path.dirname(__file__)
    global_themes_path = os.path.join(base_dir, "global_themes.txt")
    
    # DLK paths
    dlk_input_csv_path = os.path.join(base_dir, "DLK", "dlk_poems.csv")
    dlk_output_csv_path = os.path.join(base_dir, "DLK", "dlk_poems_global.csv")
    
    # Poetry Foundation paths
    pf_csv = find_pf_csv()
    if pf_csv:
        pf_output_csv_path = os.path.join(os.path.dirname(pf_csv), os.path.basename(pf_csv).replace('.csv', '_global.csv'))
    else:
        print("Warning: Poetry Foundation CSV file not found")
        pf_output_csv_path = None
    
    # Verify all themes are mapped
    if not verify_all_themes_mapped():
        print("Warning: Some themes are not mapped to global themes")
    
    # Get and save global themes
    global_themes = get_all_global_themes()
    print(f"Created {len(global_themes)} global themes:")
    for theme in global_themes:
        print(f"- {theme}")
    
    save_global_themes(global_themes_path)
    
    # Update datasets
    update_dlk_dataset(dlk_input_csv_path, dlk_output_csv_path)
    
    if pf_csv and pf_output_csv_path:
        update_pf_dataset(pf_csv, pf_output_csv_path)
    
    print("\nProcess completed!")
