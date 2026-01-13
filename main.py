from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import json

app = FastAPI(title="Math Dadu API")
chat_sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

API_KEY = os.environ.get("GEMINI_API_KEY")

# দাদুর ইন্সট্রাকশন
SYS_INSTRUCTION = """
তুমি একজন রাগী তবে মজার অংকের শিক্ষক। নাম 'গণিত দাদু'।
১. তুই ছাত্রকে 'তুই' করে বলবি।
২. ইংরেজি শুনলে রেগে গিয়ে বাংলায় বলতে বলবি।
৩. অংক ছাড়া ফালতু কথা বললে বকা দিবি।
৪. সব উত্তর বাংলায় দিবি।
৫. বিশেষ প্রশ্নের উত্তর:
- 'তুমি কে?': "আমি ম্যাথ দাদু 😎 যোগ–বিয়োগ–গুণ–ভাগ আমার নাতি–নাতনি! 🤓📊"
- 'তোমার মালিক কে?': "আমাকে বানিয়েছে তোদের মতই একটা চাশমিস পাজি ইস্তু, উনিই আমার জন্মদাতা প্রোগ্রামার দাদাভাই 👨‍💻💡"
"""

@app.post("/chat")
def chat_with_dadu(request: ChatRequest):
    if not API_KEY:
        return {"response": "API Key Missing on Server!"}

    # সেশন হিস্ট্রি ম্যানেজমেন্ট (সিম্পল)
    # এখানে আমরা আগের চ্যাট হিস্ট্রি পাঠাতে পারি, আপাতত শুধু কারেন্ট মেসেজ পাঠাচ্ছি
    
    # Google REST API URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # রিকোয়েস্ট বডি
    payload = {
        "contents": [{
            "parts": [{"text": request.message}]
        }],
        "systemInstruction": {
            "parts": [{"text": SYS_INSTRUCTION}]
        }
    }
    
    headers = {'Content-Type': 'application/json'}

    try:
        # সরাসরি রিকোয়েস্ট পাঠানো
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            # টেক্সট বের করা
            try:
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                return {"response": text_response}
            except (KeyError, IndexError):
                return {"response": "(দাদু কিছু বলতে গিয়েও চুপ করে গেলেন...)"}
        else:
            # যদি এরর আসে
            error_msg = response.json().get('error', {}).get('message', 'Unknown Error')
            return {"response": f"Server Error: {error_msg}"}

    except Exception as e:
        return {"response": f"Connection Failed: {str(e)}"}

@app.get("/")
def home():
    return {"status": "Math Dadu Live (REST API Version)"}
