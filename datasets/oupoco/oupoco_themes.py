# %%
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

df = pd.read_csv("oupoco.csv") 

with open('../global/themes/global_themes.txt', 'r') as f:
    allowed_themes = [line.strip() for line in f.readlines()]

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


theme_descriptions = {
    "Activities & Work": "themes about work, labor, profession, daily activities",
    "Arts & Culture": "themes about painting, literature, music, traditions, creativity",
    "Body & Health": "themes about the human body, health, sickness, vitality",
    "Challenge & Adversity": "themes about overcoming obstacles, struggles, hardships",
    "Complexity & Paradox": "themes about contradictions, complexities, dualities",
    "Death & Loss": "themes about death, grief, loss, mourning, endings",
    "Family & Home": "themes about family life, home, parents, children",
    "Fate & Destiny": "themes about predestined events, fate, destiny, inevitable outcomes",
    "Humor & Play": "themes about humor, fun, games, lightheartedness",
    "Identity & Self": "themes about the self, identity, self-discovery, introspection",
    "Life & Living": "themes about daily life, existence, being alive",
    "Life Cycles": "themes about birth, aging, life stages, rebirth",
    "Love & Relationships": "themes about love, romance, partnerships, heartbreak",
    "Mind & Emotions": "themes about emotional states, thoughts, mental life",
    "Miscellaneous": "miscellaneous topics that don't fit elsewhere",
    "Morality & Ethics": "themes about right and wrong, morality, ethical dilemmas",
    "Nature & Environment": "themes about nature, animals, environment, weather",
    "Places & Spaces": "themes about cities, landscapes, buildings, locations",
    "Power & Freedom": "themes about authority, power, independence, control",
    "Religion & Spirituality": "themes about religion, faith, spirituality",
    "Seasons": "themes about spring, summer, autumn, winter, seasonal changes",
    "Society & Politics": "themes about society, politics, social structures",
    "Time & Temporality": "themes about time, change, memory, past and future",
    "War & Conflict": "themes about wars, battles, conflict, peace",
    "Wisdom & Knowledge": "themes about knowledge, education, wisdom, insight",
    "Youth & Coming of Age": "themes about childhood, adolescence, growing up"
}

#
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

theme_embeddings = {theme: embedder.encode(desc) for theme, desc in theme_descriptions.items()}

def get_theme_semantic_with_boost(text):
    if not isinstance(text, str) or not text.strip():
        return "Miscellaneous"

    poem_embedding = embedder.encode(text)
    text_lower = text.lower()
    similarities = {theme: cosine_similarity([poem_embedding], [embedding])[0][0]
                    for theme, embedding in theme_embeddings.items()}

    keyword_boost = {}

    for major_theme, keywords in THEME_CATEGORIES.items():
        for keyword in keywords:
            if keyword in text_lower:
                mapped_theme = GLOBAL_THEME_MAPPING.get(major_theme, major_theme)
                if mapped_theme in allowed_themes:
                    keyword_boost[mapped_theme] = keyword_boost.get(mapped_theme, 0) + 0.05

    combined_scores = {}
    for theme, score in similarities.items():
        boost = keyword_boost.get(theme, 0)
        combined_scores[theme] = score + boost

    best_theme = max(combined_scores, key=combined_scores.get)
    return best_theme

df["theme"] = df["text"].apply(get_theme_semantic_with_boost)

df.to_csv("oupoco_themes.csv", index=False)
print("✅ Done! Saved as 'oupoco_themes.csv'")


# %%
print(df["theme"].value_counts())


# %%



