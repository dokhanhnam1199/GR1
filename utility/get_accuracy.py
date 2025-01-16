import pandas as pd
# -------------------------------------------------------------------------------------------------------------------------------------------------
# Calculate the average accuracy and find the best and worst tickers
# -------------------------------------------------------------------------------------------------------------------------------------------------
accuracy_file = "result/accuracy.csv"

# Calculate the average accuracy of all tickers
df_accuracy = pd.read_csv(accuracy_file, encoding='utf-8')
average_accuracy = df_accuracy['accuracy'].mean()
add_row = {'ticker': 'Average', 'accuracy': average_accuracy}
df_add_row = pd.DataFrame([add_row])
df_add_row.to_csv(accuracy_file, mode='a', header=False, index=False, encoding='utf-8-sig')

# Find the ticker with the highest accuracy
max_accuracy = df_accuracy['accuracy'].max()
best_ticker = df_accuracy[df_accuracy['accuracy'] == max_accuracy]['ticker'].values[0]
add_row = {'ticker': f'Best({best_ticker})', 'accuracy': max_accuracy}
df_add_row = pd.DataFrame([add_row])
df_add_row.to_csv(accuracy_file, mode='a', header=False, index=False, encoding='utf-8-sig')

# Find the ticker with the lowest accuracy
min_accuracy = df_accuracy['accuracy'].min()
worst_ticker = df_accuracy[df_accuracy['accuracy'] == min_accuracy]['ticker'].values[0]
add_row = {'ticker': f'Worst({worst_ticker})', 'accuracy': min_accuracy}
df_add_row = pd.DataFrame([add_row])
df_add_row.to_csv(accuracy_file, mode='a', header=False, index=False, encoding='utf-8-sig')