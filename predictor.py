import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
import time

# Function to get prediction from the generative AI model
def get_prediction(ticker, target_date, price_movement, summary_target, chat_session):
    # Construct the message to send to the AI model
    message = f"dựa trên tổng hợp các bài báo và lịch sử biến động giá từ ngày sau đây, dự đoán biến động giá cổ phiếu {ticker} ngày {target_date}.\n"
    message += "tổng hợp các bài báo:\n"
    for n in summary_target:
        message += f"{n[0]}. Tiêu đề: {n[1]}. Tóm tắt: {n[2]}.\n"
    message += "lịch sử biến động giá:\n"
    for p in price_movement:
        message += f"vào ngày {p[0]} giá cổ phiếu {ticker} {p[6]}.\n"
    # Send the message and get the prediction
    prediction = chat_session.send_message(message)
    return prediction.text

# -------------------------------------------------------------------------------------------------------------------------------------------------
# create a generative AI model to predict stock price movements
# -------------------------------------------------------------------------------------------------------------------------------------------------

# Load the environment variables
load_dotenv()
# Configure the generative AI model with the API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Define the generation configuration for the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the generative AI model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="dự đoán biến động giá cổ phiếu theo yêu cầu. câu trả lời chỉ là tăng hoặc giảm, không giả thích gì thêm.",
)

# Start a chat session with the model
chat_session = model.start_chat()

# -------------------------------------------------------------------------------------------------------------------------------------------------
# Generate predictions for a stock
# -------------------------------------------------------------------------------------------------------------------------------------------------

# create accuracy file to store prediction accuracy
accuracy_file = "result/accuracy.csv"
if not os.path.exists(accuracy_file):
    df_accuracy = pd.DataFrame(columns=['ticker', 'accuracy'])
    df_accuracy.to_csv(accuracy_file, index=False, encoding='utf-8-sig')

k = 5  # Number of days to consider for prediction
df = pd.read_csv('data/VN30.csv', encoding='utf-8')
vn30 = df['Ticker'].tolist() # List of tickers in the VN30 index

# Loop through each ticker in the VN30 list
for ticker in vn30:
    prediction_file = f"result/prediction/{ticker}.csv"  # File to save predictions

    # Create the prediction file if it doesn't exist
    if not os.path.exists(prediction_file):
        df = pd.DataFrame(columns=['time', 'prediction'])
        df.to_csv(prediction_file, index=False, encoding='utf-8-sig')

    # Load the summary and price data
    summary = pd.read_csv(f"data/summary/{ticker}.csv")
    price = pd.read_csv(f"data/price/{ticker}.csv")

    # Convert price data to a list of lists
    price_list = price.values.tolist()

    # Loop through the price data to generate predictions
    for i in range(k, len(price_list)):
        target_date = price_list[i][0]  # Target date for prediction
        price_movement = price_list[i-k:i]  # Price movement data for the past k days
        summary_target = []  # List to store relevant news summaries

        # Collect news summaries for the past k days
        for i in range(1, k + 1):
            date = datetime.strptime(target_date, "%Y-%m-%d").date() - timedelta(days=i)
            date = date.strftime('%Y-%m-%d')
            if not summary[summary['publish_date'] == date].empty:
                summary_target += summary[summary['publish_date'] == date].values.tolist()

        # Try to get the prediction and save it to the file
        while True:
            try:
                prediction = get_prediction(ticker, target_date, price_movement, summary_target, chat_session)
                prediction = prediction.strip()
                new_row = {'time': target_date, 'prediction': prediction}
                df_new_row = pd.DataFrame([new_row])
                df_new_row.to_csv(prediction_file, mode='a', header=False, index=False, encoding='utf-8-sig')
                print(f"Prediction for {ticker} on {target_date} is {prediction}.")
                time.sleep(4.1)
                break  # Exit the loop if successful
            except Exception as e:
                print(f"An error occurred: {e}. Retrying in 1 minute...")
                time.sleep(60)  # Wait for 1 minute before retrying

    # -------------------------------------------------------------------------------------------------------------------------------------------------
    # Calculate the accuracy of the predictions
    # -------------------------------------------------------------------------------------------------------------------------------------------------

    # Load the prediction file
    prediction = pd.read_csv(prediction_file, encoding='utf-8')

    # Initialize a list to store comparison results
    comparison_results = []

    # Compare each prediction with the actual price change
    for i in range(len(prediction)):
        prediction_value = prediction.loc[i, 'prediction']
        price_change = price.loc[i + k, 'change']
        comparison_results.append(prediction_value == price_change)

    # Count the number of correct and incorrect predictions
    true = comparison_results.count(True)
    false = comparison_results.count(False)

    # Calculate the accuracy
    accuracy = true / (true + false)

    # Append the accuracy to accuracy.csv
    new_row = {'ticker': ticker, 'accuracy': accuracy}
    df_new_row = pd.DataFrame([new_row])
    df_new_row.to_csv(accuracy_file, mode='a', header=False, index=False, encoding='utf-8-sig')
    
    print(f"Predictions for {ticker} have been generated with accuracy {accuracy}.")

# -------------------------------------------------------------------------------------------------------------------------------------------------
# Calculate the average accuracy and find the best and worst tickers
# -------------------------------------------------------------------------------------------------------------------------------------------------

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