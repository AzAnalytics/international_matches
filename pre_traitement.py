import pandas as pd

df = pd.read_csv("all_matches.csv", sep=",")

last_date = df['date'].iloc[-1]
print(last_date)