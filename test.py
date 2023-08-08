import pandas as pd

df = pd.DataFrame(columns=["1", "2", "3"])

data = (4, 5, 6)
df.loc[len(df)] = data
data2 = (4, 5, 6)
df.loc[len(df)] = data

print(df)