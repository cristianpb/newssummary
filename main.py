import os
import json
import requests
from openai import OpenAI

# --- CONFIGURATION ---
NEWS_API_KEY = os.environ.get("NEWSAPI_KEY")
OPENAI_API_KEY = os.environ.get("GROQ_API_KEY")
KEYWORDS = json.loads(os.environ.get("KEYWORDS", '[]'))
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

def fetch_news_with_sources(keyword):
    """Fetch news and return a formatted string with titles and URLs."""
    url = f"https://newsapi.org/v2/everything?q={keyword}&pageSize=5&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get('articles', [])
    
    formatted_data = ""
    for art in articles:
        source_name = art['source']['name']
        title = art['title']
        link = art['url']
        desc = art.get('description', 'No description available.')
        
        formatted_data += f"SOURCE: {source_name}\nTITLE: {title}\nURL: {link}\nSUMMARY: {desc}\n\n"
    
    return formatted_data

def generate_resume_with_citations(news_content):
    """LLM summarizes news and explicitly includes source links."""
    prompt = (
        "Create a professional news resume in english based on the data below. "
        "For every news item, include a brief summary in english and the source name with its URL. "
        "Format it using Telegram-friendly Markdown (e.g., [Source Name](URL)).\n\n"
        f"{news_content}"
    )
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are a research assistant that provides cited news summaries."},
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
        print(f"📡 Gathering news for {keyword}...")
        content_for_llm = fetch_news_with_sources(keyword)
        
        if content_for_llm:
            print("🧠 Synthesizing summary with citations...")
            final_report = generate_resume_with_citations(content_for_llm)
            
            print("📤 Sending to Telegram...")
            # Adding a header to the final message
            full_message = f"📰 *Latest Updates: {keyword}*\n\n{final_report}"
            print(full_message)
            #status = send_telegram_msg(f"✨ *Daily Briefing: {keyword}*\n\n{summary}")
            
            #if status == 200:
            #    print("✅ Success! Check your Telegram.")
            #else:
            #    print(f"❌ Failed to send message. Status: {status}")
        else:
            print("⚠️ No news found for that keyword.")


https://www.n-tv.de/politik/21-45-IAEA-Chef-mahnt-zur-schnellen-Reparatur-der-Tschernobyl-Schutzanlage-id30757737.html
