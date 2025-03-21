import pandas as pd
import json
from find_author_location import get_author_city
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Load JSON (assuming it's already converted from XML using xq)
with open("sonnets_oupoco_tei.json", "r", encoding="utf-8") as f:
    data = json.load(f)['teiCorpus']['TEI']

# Extract poetry content
poems = []

def process_poem(anthology, poem):
    """Process a single poem entry."""
    if type(poem) != dict:
        print(anthology["teiHeader"])
        print(poem)
        exit(1)

    poem = poem["body"]["div"]

    # Fill in missing values
    if poem["docAuthor"] == {}:
        poem["docAuthor"] = {"#text": "Unknown", "@sex": "Unknown"}

    title = poem["head"].strip()
    author = poem["docAuthor"]["#text"].strip()

    sex = poem["docAuthor"]["@sex"].strip().upper()
    if sex == "H":  # Fix French stuff
        sex = "M"

    date = poem["docDate"].strip()
    if "-" in date:  # Get midpoint of date ranges
        dates = [int(x.strip()) for x in date.split("-")]
        date = sum(dates) / len(dates)
    date = int(date)

    text = "\n".join(l['#text'] for lg in poem["lg"] for l in lg["l"])

    found, city = get_author_city(author)
    
    return {"title": title, "author": author, "sex": sex, "date": date, "city": city if found else "Unknown", "language": "FR", "text": text}

# Process anthologies in parallel
with ThreadPoolExecutor() as executor:
    futures = []
    for anthology in tqdm(data, desc="Processing Anthologies", position=0):
        if type(anthology["text"]) != list:
            anthology["text"] = [anthology["text"]]
        
        for poem in anthology["text"]:
            futures.append(executor.submit(process_poem, anthology, poem))
    
    for future in tqdm(futures, desc="Processing Poems", leave=True, position=0):
        poems.append(future.result())

# Convert to DataFrame
df = pd.DataFrame(poems)

# Display the first few rows
print(df.head())

# Save to CSV
df.to_csv("oupoco.csv")

