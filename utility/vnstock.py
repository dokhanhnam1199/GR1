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
    stock = Vnstock().stock(symbol=ticker, source='TCBS')
    df = stock.quote.history(start='2024-01-01', end='2024-12-06')
    df['change'] = df.apply(lambda row: 'Tăng' if row['close'] > row['open'] else 'Giảm', axis=1)
    df.to_csv(file_name, index=False)
    print(f"Extracted {ticker} price history to {file_name}")


