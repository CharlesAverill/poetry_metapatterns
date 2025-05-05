import pandas as pd
import json
from author_info import get_author_city
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Load JSON (assuming it's already converted from XML using xq)
with open("data.json", "r", encoding="utf-8") as f:
    data = [x for x in json.load(f) if x[0]["Language"][0] in ["English", "French", "German"] and x[0].get("Author", None) and x[0].get("Author Birth", None)]

print("Loaded data")
# Extract poetry content
poems = []

def process_poem(poem):
    """Process a single poem entry."""
    metadata, text = poem

    author = metadata["Author"][0]
    found, city, sex = get_author_city(author)
    if not found:
        return None
    city = city if found else "Unknown"
    title = metadata["Title"][0]
    try:
        date = (int(metadata["Author Birth"][0]) + 20)
    except:
        date = "Unknown"
    language = "EN" if metadata["Language"] == ["English"] else ("FR" if metadata["Language"] == ["French"] else "DE")
    return {"title": title, "author": author, "sex": sex, "date": date, "city": city, "language": language, "text": text}

"""
# Process anthologies in parallel
with ThreadPoolExecutor() as executor:
    futures = []
    for poem in tqdm(data):
        futures.append(executor.submit(process_poem, poem))
    
    for future in tqdm(futures, desc="Processing Poems", leave=True, position=0):
        poems.append(future.result())
"""

print(len(data))
exit()

for x in tqdm(data, desc="Processing Poems", leave=True, position=0):
    y = process_poem(x)
    if y:
        poems.append(y)
# Convert to DataFrame
df = pd.DataFrame(poems)

# Display the first few rows
print(df.head())

# Save to CSV
df.to_csv("gutenberg.csv", escapechar='\\')
