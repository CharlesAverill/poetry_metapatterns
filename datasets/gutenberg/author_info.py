import wikipediaapi
import spacy
from collections import Counter

# Load SpaCy NLP model once to avoid reloading on every function call
nlp = spacy.load("en_core_web_sm")

with open("countries.txt") as file:
    countries = [c.upper() for c in file.read().split("\n")]

with open("uk_cities.txt") as file:
    fr_cities = [x.strip().upper() for x in file.readlines()]

def get_author_city(author_name, wiki_wiki=None):
    if wiki_wiki is None:
        wiki_wiki = wikipediaapi.Wikipedia(user_agent='poetry_metadata/1.0 (charles@utdallas.edu)')  # Specify user agent
    
    page = wiki_wiki.page(author_name)
    
    if not page.exists():
        return False, f"Wikipedia page for '{author_name}' not found.", "Unknown"
    
    doc = nlp(page.text)
    
    # Extract locations using named entity recognition (NER)
    locations = Counter([ent.text for ent in doc.ents if ent.label_ == "GPE" and ent.text.upper() not in countries and ent.text.upper() in fr_cities]).most_common(1)  # GPE = Geopolitical Entity (Cities, Countries, etc.)
    if locations:
        locations = locations[0][0]
    else:
        return False, "", ""

    try:
        sex = "M" if Counter([ent.text for ent in doc if ent.text.lower() in ["he", "she"]]).most_common(1)[0][0] == "he" else "F"
    except:
        sex = "Unknown"

    return bool(locations), locations, sex

# Example usage
if __name__ == "__main__":
    author = input("Enter author's name: ")
    city = get_author_city(author)
    print(f"{author} primarily lived in: {city}")

