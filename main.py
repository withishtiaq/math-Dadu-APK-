from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from duckduckgo_search import DDGS
import os

app = FastAPI(title="Math Dadu API")

# ডাটা মডেল
class ChatRequest(BaseModel):
    session_id: str
    message: str

# API Key সেটআপ
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# দাদুর পার্সোনা (System Instruction)
sys_instruction = """
তুমি একজন রাগী তবে মজার অংকের শিক্ষক। নাম 'গণিত দাদু'।
১. তুই ছাত্রকে 'তুই' করে বলবি। ২. ইংরেজি শুনলে রেগে বাংলায় বলতে বলবি।
৩. অংক ছাড়া ফালতু কথা বললে বকা দিবি। ৪. সব উত্তর বাংলায় দিবি।
৫. 'তুমি কে?': "আমি ম্যাথ দাদু 😎 যোগ–বিয়োগ–গুণ–ভাগ আমার নাতি–নাতনি!"
৬. 'মালিক কে?': "আমাকে বানিয়েছে তোদের মতই একটা চাশমিস পাজি ইস্তু, উনিই আমার প্রোগ্রামার দাদাভাই 👨‍💻"
"""

@app.post("/chat")
def chat_with_dadu(request: ChatRequest):
    if not API_KEY:
        return {"response": "API Key Missing on Server!"}

    try:
        # ✅ SOLUTION: 'gemini-flash-latest' ব্যবহার করা হলো (এটি আপনার লিস্টে আছে এবং ফ্রি)
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=sys_instruction
        )
        
        # চ্যাট শুরু
        chat = model.start_chat(history=[])
        response = chat.send_message(request.message)
        
        return {"response": response.text}

    except Exception as e:
        # যদি কোনো কারণে লিমিট শেষ হয়, সুন্দর মেসেজ দেওয়া
        if "429" in str(e):
             return {"response": "বড্ড বকবক করছিস! আজকের মত ক্লাশ শেষ, আবার কালকে আসিস। এখন তোদের জন্য অনেক অংক আবিষ্কার করতে বসব!"}
        return {"response": f"Error: {str(e)}"}

@app.get("/")
def home():
    return {"status": "Math Dadu Live (Flash Latest Version)"}
