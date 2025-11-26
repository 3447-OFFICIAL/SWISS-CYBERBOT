import os
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import google.generativeai as genai

# --- CONFIGURATION ---
app = Flask(__name__)

# 🔑 API KEY (Uses the one from your previous context)
HARDCODED_API_KEY = "AIzaSyAZedPxlmgEhquH3rUfBdZk6X0DC4GlQ_o"
genai.configure(api_key=HARDCODED_API_KEY)

# 🌐 TARGET URL
TARGET_URL = "https://www.ncsc.admin.ch/ncsc/en/home.html"

# --- GLOBAL KNOWLEDGE CONTEXT ---
# We store scraped data globally so we don't scrape on every request (speed optimization)
KNOWLEDGE_BASE = {
    "scraped_content": "",
    "static_context": """
    PRIMARY PORTAL: National Cyber Security Centre (NCSC)
    - Link: https://www.ncsc.admin.ch/ncsc/en/home.html
    - Function: Swiss federal government's competence centre for cybersecurity.
    - Key Tools: Incident Reporting Form, Cyber Security Hub (CSH).
    
    SWISS LAWS:
    1. FADP/nFADP: Federal Act on Data Protection (Sept 2023). Aligns with GDPR.
    2. NCSC Mandates: Mandatory reporting for critical infra (April 2025).
    3. FINMA Circular 2023/1: ICT risk management for banks.
    """
}

def scrape_website_on_start():
    """Scrapes the NCSC website once when the server starts."""
    print(f"🕷️ Scraper: Connecting to {TARGET_URL}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Cleanup
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.extract()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        KNOWLEDGE_BASE["scraped_content"] = cleaned_text[:10000] # Limit size
        print("✅ Scraper: Success! Knowledge base updated.")
        
    except Exception as e:
        print(f"❌ Scraper: Failed. {e}")
        KNOWLEDGE_BASE["scraped_content"] = "Live data unavailable. Using static context only."

# --- GEMINI AI HANDLER ---
def generate_ai_response(user_query):
    """Sends the context + query to Gemini."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        
        full_context = f"""
        You are the 'Swiss CyberBot' for Dialogflow.
        
        CONTEXT SOURCE 1 (Static):
        {KNOWLEDGE_BASE['static_context']}
        
        CONTEXT SOURCE 2 (Live Scrape):
        {KNOWLEDGE_BASE['scraped_content']}
        
        INSTRUCTIONS:
        Answer the User Query based strictly on the context above.
        Keep answers concise (under 200 words) as they are for a chat interface.
        If the user asks for circulars, mention "I can fetch those documents for you."
        """
        
        response = model.generate_content(f"{full_context}\n\nUser Query: {user_query}")
        return response.text
    except Exception as e:
        return f"I encountered an error analyzing the data: {str(e)}"

# --- WEBHOOK ROUTE ---
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    
    # 1. Extract Intent and Query
    try:
        intent_name = req.get('queryResult').get('intent').get('displayName')
        user_query = req.get('queryResult').get('queryText')
    except AttributeError:
        return jsonify({"fulfillmentText": "Error parsing Dialogflow request."})

    response_text = ""

    # 2. Route Logic based on Intent
    if intent_name == "AskQuestion":
        # The main AI logic
        response_text = generate_ai_response(user_query)

    # UPDATED: Checks for "Download circulars" OR "GetCirculars"
    elif intent_name in ["GetCirculars", "Download circulars"]:
        # Hardcoded logic matching the Streamlit app
        response_text = (
            "Here are the latest Swiss Cyber Circulars:\n"
            "1. 📄 NCSC Semi-Annual Report 2024 (PDF)\n"
            "2. 📄 FINMA Circular 2023/1 Ops Risks\n"
            "3. 📄 nFADP Implementation Checklist\n\n"
            "Visit ncsc.admin.ch for the full downloads."
        )

    elif intent_name == "Default Welcome Intent":
        response_text = (
            "Grüezi! I am the Swiss CyberBot. "
            "I'm connected to the NCSC live feed. "
            "Ask me about FADP, Reporting Incidents, or recent alerts."
        )

    else:
        # Debugging helper: Tells you exactly what intent name it received
        response_text = f"Intent '{intent_name}' not recognized in backend code. Please check dialogflow_webhook.py"

    # 3. Return Dialogflow Response
    return jsonify({
        "fulfillmentText": response_text
    })

if __name__ == '__main__':
    # Initialize data
    scrape_website_on_start()
    # Run server
    app.run(debug=True, port=5000)