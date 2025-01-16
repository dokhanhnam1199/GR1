import pandas as pd

df = pd.read_csv("result/accuracy.csv")  # Read the CSV file
a = df['accuracy'].tolist()  # Convert the column to a list
t = df['ticker'].tolist()  # Convert the column to a list
a = [round(x*100, 2) for x in a]  # Round the values to 2 decimal places
for i in range(len(a)):
    print(t[i])  # Print the values


