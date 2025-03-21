import pandas as pd

with open("fr_cities.txt") as file:
    fr_cities = [x.strip() for x in file.readlines()]

df = pd.read_csv("oupoco.csv")

unknown_count = (df['city'] == 'Unknown').sum()
other_count = len(df[(df['city'] != 'Unknown') & (df['city'].isin(fr_cities))])

# Compute the ratio
print("Known city ratio:", other_count / len(df))

print([x for x in set(df['city']) if x in fr_cities])
