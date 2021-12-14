import pandas
from pathlib import Path

folder_results = Path("results/")
folder_results = str(folder_results) + "/"

df = pandas.read_csv('hrdata.csv')
print(df)