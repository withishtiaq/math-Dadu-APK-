from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import json

app = FastAPI(title="Math Dadu API")

class ChatRequest(BaseModel):
    session_id: str
    message: str

API_KEY = os.environ.get("GEMINI_API_KEY")

# দাদুর পার্সোনা (System Instruction)
# Gemini Pro তে System Instruction আলাদাভাবে সাপোর্ট করে না, তাই আমরা প্রম্পটের সাথে মিশিয়ে দেব।
DADU_PERSONA = """
তুমি একজন রাগী তবে মজার অংকের শিক্ষক। নাম 'গণিত দাদু'।
১. তুই ছাত্রকে 'তুই' করে বলবি।
২. ইংরেজি শুনলে রেগে গিয়ে বাংলায় বলতে বলবি।
৩. অংক ছাড়া ফালতু কথা বললে বকা দিবি।
৪. সব উত্তর বাংলায় দিবি।
৫. যদি জিজ্ঞেস করে 'তুমি কে?': বলবি "আমি ম্যাথ দাদু 😎 যোগ–বিয়োগ–গুণ–ভাগ আমার নাতি–নাতনি! 🤓📊"
৬. যদি জিজ্ঞেস করে 'তোমার মালিক কে?': বলবি "আমাকে বানিয়েছে তোদের মতই একটা চাশমিস পাজি ইস্তু, উনিই আমার জন্মদাতা প্রোগ্রামার দাদাভাই 👨‍💻💡"

ছাত্রের প্রশ্ন: 
"""

@app.post("/chat")
def chat_with_dadu(request: ChatRequest):
    if not API_KEY:
        return {"response": "API Key Missing on Server!"}

    # URL পরিবর্তন করে 'gemini-pro' দেওয়া হয়েছে (এটি ১০০% কাজ করবে)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
    
    # প্রম্পট তৈরি (পার্সোনা + প্রশ্ন)
    final_prompt = DADU_PERSONA + request.message

    # রিকোয়েস্ট বডি
    payload = {
        "contents": [{
            "parts": [{"text": final_prompt}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            try:
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                return {"response": text_response}
            except (KeyError, IndexError):
                return {"response": "(দাদু কিছু বলতে গিয়েও চুপ করে গেলেন...)"}
        else:
            # এরর ডিবাগিং
            error_msg = response.json().get('error', {}).get('message', 'Unknown Error')
            return {"response": f"Server Error: {error_msg}"}

    except Exception as e:
        return {"response": f"Connection Failed: {str(e)}"}

@app.get("/")
def home():
    return {"status": "Math Dadu is Live (Gemini Pro Version)"}
