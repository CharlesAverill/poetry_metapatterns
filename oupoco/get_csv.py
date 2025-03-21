import pandas as pd
import json

# Load JSON (assuming it's already converted from XML using xq)
with open("sonnets_oupoco_tei.json", "r", encoding="utf-8") as f:
    data = json.load(f)['teiCorpus']['TEI']

# Extract poetry content
poems = []
for anthology in data:
    if type(anthology["text"]) != list:
        anthology["text"] = [anthology["text"]]

    for poem in anthology["text"]:
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
        if sex == "H": # Fix french stuff
            sex = "M"

        date = poem["docDate"].strip()
        if "-" in date: # Get midpoint of date ranges
            dates = [int(x.strip()) for x in date.split("-")]
            date = sum(dates) / len(dates)
        date = int(date)

        text = ""
        for lg in poem["lg"]:
            for l in lg["l"]:
                text += f"{l['#text']}\n"

        poems.append({"title": title, "author": author, "sex": sex, "date": date, "text": text, "language": "FR"})

# Convert to DataFrame
df = pd.DataFrame(poems)

# Display the first few rows
print(df.head())

df.to_csv("oupoco.csv")
