import csv
from vnstock3 import Vnstock
import pandas as pd

csv_file = "data/VN30.csv"
vn30 = []

with open(csv_file, mode="r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        vn30.append(row[0])  # Append values from the column

for ticker in vn30:
    file_name = f"data/price/{ticker}.csv"
    df = pd.read_csv(file_name)
    df['change'] = df.apply(lambda row: 'rose' if row['close'] > row['open'] else 'fell', axis=1)
    df.to_csv(file_name, index=False)


