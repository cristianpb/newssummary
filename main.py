import os
import requests
from openai import OpenAI

# --- CONFIGURATION ---
NEWS_API_KEY = os.environ.get("NEWSAPI_KEY")
OPENAI_API_KEY = os.environ.get("GROQ_API_KEY")
KEYWORDS = os.environ.get("KEYWORDS", [])
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

def fetch_news(keyword):
    """Fetch recent articles from NewsAPI based on a keyword."""
    url = f"https://newsapi.org/v2/everything?q={keyword}&pageSize=5&sortBy=relevancy&apiKey={NEWS_API_KEY}"
    print(url)
    response = requests.get(url)
    articles = response.json().get('articles', [])
    
    # Combine titles and descriptions for the LLM
    news_text = ""
    for idx, art in enumerate(articles):
        news_text += f"{idx+1}. {art['title']}: {art['description']}\n\n"
    return news_text

def generate_resume(news_content):
    """Use an LLM to summarize the news into a 'briefing' or resume format."""
    prompt = f"Summarize the following news articles into a professional daily briefing:\n\n{news_content}"
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are a news curator. Create a concise executive summary."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def send_telegram_msg(text):
    """Send the final summary via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.status_code

# --- EXECUTION ---
if __name__ == "__main__":
    for keyword in KEYWORDS:
        print(f"🔍 Fetching news for: {keyword}...")
        raw_news = fetch_news(keyword)
        
        if raw_news:
            print("🤖 Generating LLM summary...")
            summary = generate_resume(raw_news)
            
            print("📤 Sending Telegram notification...")
            print(summary)
            #status = send_telegram_msg(f"✨ *Daily Briefing: {keyword}*\n\n{summary}")
            
            #if status == 200:
            #    print("✅ Success! Check your Telegram.")
            #else:
            #    print(f"❌ Failed to send message. Status: {status}")
        else:
            print("⚠️ No news found for that keyword.")
