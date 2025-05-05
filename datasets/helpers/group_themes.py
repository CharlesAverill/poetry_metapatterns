"""
Script to group similar themes from the DLK dataset into fewer categories
and update both the unique themes file and the original dataset.
"""

import csv
import os
import re
from collections import defaultdict

# Major theme categories
THEME_CATEGORIES = {
    "Nature": ["nature", "seasons", "weather", "landscape", "animal", "plant", "flower", "tree", "bird", "forest", "garden", 
              "mountain", "river", "sea", "ocean", "sky", "sun", "moon", "star", "light", "darkness", "winter", "summer", 
              "spring", "autumn", "fall", "earth", "water", "fire", "air"],
    
    "Love": ["love", "passion", "desire", "romance", "heart", "affection", "intimacy", "attachment", "devotion", "longing", 
            "yearning", "relationship", "union", "marriage", "wedding", "spouse", "lover", "beloved", "cupid", "eros", 
            "amor", "unrequited", "courtship"],
    
    "Death": ["death", "mortality", "funeral", "grave", "tomb", "dying", "afterlife", "cemetery", "memorial", "eulogy", 
             "mourning", "grief", "loss", "bereavement", "farewell", "goodbye", "passing", "eternal rest", "memorial"],
    
    "Time": ["time", "passing", "age", "aging", "youth", "memory", "remembrance", "nostalgia", "past", "present", "future", 
            "eternity", "moment", "fleeting", "ephemeral", "transient", "temporary", "perpetual", "eternal", "history", 
            "change", "impermanence"],
    
    "Religion": ["god", "divine", "faith", "prayer", "worship", "spiritual", "holy", "sacred", "religion", "church", 
               "heaven", "paradise", "salvation", "soul", "spirit", "angel", "christ", "jesus", "christian", "bible", 
               "blessing", "miracle", "providence", "creation", "creator"],
    
    "Wisdom": ["wisdom", "knowledge", "truth", "insight", "understanding", "learning", "education", "philosophy", 
              "thought", "reason", "intellect", "mind", "contemplation", "reflection", "meditation", "enlightenment", 
              "awareness", "consciousness", "realization"],
    
    "Virtue": ["virtue", "morality", "ethics", "goodness", "kindness", "compassion", "mercy", "forgiveness", "charity", 
              "justice", "fairness", "honor", "integrity", "honesty", "loyalty", "fidelity", "duty", "responsibility", 
              "conscience", "humility"],
    
    "Vice": ["vice", "sin", "evil", "wickedness", "corruption", "greed", "avarice", "lust", "gluttony", "sloth", "wrath", 
            "anger", "pride", "vanity", "envy", "jealousy", "hatred", "malice", "cruelty", "dishonesty", "betrayal", 
            "treachery", "deceit"],
    
    "Freedom": ["freedom", "liberty", "independence", "autonomy", "emancipation", "release", "escape", "liberation", 
               "free will", "choice", "decision", "determination", "self-determination"],
    
    "Joy": ["joy", "happiness", "pleasure", "delight", "bliss", "ecstasy", "euphoria", "gladness", "cheer", "merriment", 
           "celebration", "festivity", "jubilation", "exultation", "elation", "enjoyment", "satisfaction", "content"],
    
    "Sorrow": ["sorrow", "sadness", "misery", "melancholy", "gloom", "despair", "anguish", "grief", "pain", "suffering", 
              "agony", "torment", "distress", "affliction", "woe", "lament", "mourning", "regret", "remorse"],
    
    "War": ["war", "battle", "conflict", "combat", "fight", "struggle", "strife", "violence", "hostility", "aggression", 
           "attack", "defense", "enemy", "opponent", "victory", "defeat", "conquest", "resistance", "peace"],
    
    "Art": ["art", "poetry", "music", "painting", "sculpture", "dance", "theater", "literature", "creativity", "imagination", 
           "inspiration", "expression", "aesthetic", "beauty", "creation", "composition", "performance", "artist", "poet"],
    
    "Society": ["society", "community", "civilization", "culture", "tradition", "custom", "heritage", "history", "politics", 
               "government", "authority", "power", "class", "status", "hierarchy", "social", "public", "private", "family"],
    
    "Self": ["self", "identity", "individuality", "personality", "character", "ego", "soul", "spirit", "mind", "body", 
            "existence", "being", "essence", "nature", "consciousness", "awareness", "perception", "reflection"],
    
    "Fate": ["fate", "destiny", "fortune", "luck", "chance", "coincidence", "providence", "kismet", "karma", "predestination", 
            "determination", "doom", "lot", "future", "prophecy", "omen", "portent", "sign"],
    
    "Life": ["life", "living", "existence", "vitality", "vigor", "energy", "strength", "health", "growth", "development", 
            "maturity", "progress", "journey", "path", "adventure", "experience", "reality", "birth", "rebirth"],
    
    "Hope": ["hope", "optimism", "expectation", "anticipation", "aspiration", "ambition", "dream", "desire", "wish", 
            "longing", "yearning", "faith", "trust", "confidence", "encouragement", "assurance", "promise", "prospect"],
    
    "Fear": ["fear", "anxiety", "worry", "concern", "dread", "terror", "horror", "panic", "alarm", "apprehension", 
            "trepidation", "foreboding", "misgiving", "suspicion", "doubt", "uncertainty", "insecurity", "threat"],
    
    "Power": ["power", "strength", "might", "force", "energy", "vigor", "influence", "authority", "control", "dominance", 
             "supremacy", "command", "rule", "leadership", "sovereignty", "mastery", "superiority", "domination"],

    "Human Experience": ["human", "experience", "condition", "existence", "life", "reality", "perception", "sensation", 
                      "emotion", "feeling", "thought", "idea", "concept", "belief", "opinion", "view", "perspective", 
                      "attitude", "mind", "heart", "soul", "spirit", "body", "flesh", "blood", "breath", "voice", "silence"]
}

def load_unique_themes(themes_file_path):
    themes = []
    try:
        with open(themes_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                theme = line.strip()
                if theme:
                    themes.append(theme)
        return themes
    except Exception as e:
        print(f"Error loading themes: {e}")
        return []

def categorize_theme(theme, categories):
    theme_lower = theme.lower()
    theme_clean = re.sub(r'["\'\.,\(\)]', '', theme_lower).strip()
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', theme_clean):
                return category
    
    # Handle German themes and other special cases
    if any(german_word in theme_lower for german_word in ['gott', 'himmel', 'seele', 'liebe', 'tod', 'leben', 'natur']):
        # German religious/spiritual concepts
        if any(word in theme_lower for word in ['gott', 'himmel', 'heilig', 'geist', 'seele', 'glauben']):
            return "Religion"
        # German love terms
        if any(word in theme_lower for word in ['liebe', 'herz', 'liebende']):
            return "Love"
        # German death terms
        if any(word in theme_lower for word in ['tod', 'sterben', 'grab']):
            return "Death"
        # German nature terms
        if any(word in theme_lower for word in ['natur', 'wald', 'blume', 'garten']):
            return "Nature"
    
    # Catch additional themes that might be missed
    if "accept" in theme_lower or "resign" in theme_lower:
        return "Acceptance"
    if "loss" in theme_lower or "absent" in theme_lower:
        return "Loss"
    if "youth" in theme_lower or "child" in theme_lower:
        return "Youth"
    if "absurd" in theme_lower or "meaning" in theme_lower:
        return "Existentialism"
    if "friend" in theme_lower:
        return "Friendship"
    if "lone" in theme_lower or "alone" in theme_lower or "solitude" in theme_lower:
        return "Solitude"
    
    # Default category for uncategorized themes
    return "Miscellaneous"

def group_themes(themes, categories):
    theme_mapping = {}
    grouped_themes = defaultdict(list)
    
    for theme in themes:
        category = categorize_theme(theme, categories)
        theme_mapping[theme] = category
        grouped_themes[category].append(theme)
    
    return theme_mapping, grouped_themes

def save_grouped_themes(output_path, grouped_themes):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write the categories first (one per line)
            for category in sorted(grouped_themes.keys()):
                f.write(f"{category}\n")
            
            print(f"Successfully saved {len(grouped_themes)} theme categories to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving grouped themes: {e}")
        return False

def update_dataset(input_csv_path, output_csv_path, theme_mapping):
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
                    if original_tag and original_tag in theme_mapping:
                        row[6] = theme_mapping[original_tag]
                
                csv_writer.writerow(row)
                
        print(f"Successfully updated dataset and saved to {output_csv_path}")
        return True
    except Exception as e:
        print(f"Error updating dataset: {e}")
        return False

def save_theme_mapping(mapping_path, theme_mapping):
    try:
        with open(mapping_path, 'w', encoding='utf-8') as f:
            for original, category in sorted(theme_mapping.items()):
                f.write(f"{original} -> {category}\n")
            
        print(f"Successfully saved theme mapping to {mapping_path}")
        return True
    except Exception as e:
        print(f"Error saving theme mapping: {e}")
        return False

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    dlk_dir = os.path.join(base_dir, "DLK")
    
    input_themes_path = os.path.join(dlk_dir, "unique_themes.txt")
    output_grouped_themes_path = os.path.join(dlk_dir, "grouped_themes.txt")
    theme_mapping_path = os.path.join(dlk_dir, "theme_mapping.txt")
    
    input_csv_path = os.path.join(dlk_dir, "dlk_poems.csv")
    output_csv_path = os.path.join(dlk_dir, "dlk_poems_updated.csv")
    
    themes = load_unique_themes(input_themes_path)
    print(f"Loaded {len(themes)} unique themes")
    
    # Group themes into categories
    theme_mapping, grouped_themes = group_themes(themes, THEME_CATEGORIES)
    
    
    print("\nTheme categories and counts:")
    for category, themed_list in sorted(grouped_themes.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"{category}: {len(themed_list)} themes")
    
   
    save_grouped_themes(output_grouped_themes_path, grouped_themes)
    
   
    save_theme_mapping(theme_mapping_path, theme_mapping)
  
    update_dataset(input_csv_path, output_csv_path, theme_mapping)
    
    print("\nProcess completed!")
