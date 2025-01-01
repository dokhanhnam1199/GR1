import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd
import time

# -------------------------------------------------------------------------------------------------------------------------------------------------
# create a generative AI model to predict stock price movements
# -------------------------------------------------------------------------------------------------------------------------------------------------

# Load environment variables from a .env file
load_dotenv()

# Configure the generative AI model with the API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Define the configuration for the generative model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

# Initialize the generative model with the specified configuration
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-8b",
  generation_config=generation_config,
)

# Start a chat session with the model
chat_session = model.start_chat()

# -------------------------------------------------------------------------------------------------------------------------------------------------
# Generate summaries for news articles
# -------------------------------------------------------------------------------------------------------------------------------------------------

# Read the list of tickers from the VN30.csv file
df = pd.read_csv('data/VN30.csv', encoding='utf-8')
vn30 = df['Ticker'].tolist()

# Loop through each ticker in the VN30 list
for ticker in vn30:
    # Create the summary file for the current ticker
    summary_file = f"data/summary/{ticker}.csv"
    df_summary = pd.DataFrame(columns=['publish_date', 'title', 'summary'])
    df_summary.to_csv(summary_file, index=False, encoding='utf-8-sig')

    # Read the news data for the current ticker
    file_name = f"data/news/{ticker}.csv"
    df = pd.read_csv(file_name, encoding='utf-8')
    publish_date = df['publish_date'].tolist()
    title = df['title'].tolist()
    content = df['content'].tolist()

    # Loop through each news article for the current ticker
    for i in range(len(publish_date)):
        # Create the message to be sent to the generative model
        message = f"Tóm tắt bài báo sau\nTiêu đề: {title[i]}\nNội dung: {content[i]}"
        
        try:
            # Get the summary from the generative model
            summary = chat_session.send_message(message)
            summary_text = summary.text.replace('\n', ' ')

            # Create a new row with the summary data
            new_row = {'publish_date': publish_date[i], 'title': title[i], 'summary': summary_text}

            # Append the new row to the summary CSV file
            df_new_row = pd.DataFrame([new_row])
            df_new_row.to_csv(summary_file, mode='a', header=False, index=False, encoding='utf-8-sig')
            print("added row " + str(i))

            # Sleep for a short duration to avoid hitting rate limits
            time.sleep(4.1)
        except Exception as e:
            print(f"An error occurred: {e}. Retrying in 1 minute...")
            time.sleep(60)
            # Retry the current iteration
            i -= 1
  
    print("done " + str(ticker))