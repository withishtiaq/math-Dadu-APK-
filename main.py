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

# দাদুর পার্সোনা
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
        # ১. প্রথমে আমরা 'gemini-1.5-flash' দিয়ে চেষ্টা করব (সবচেয়ে ফাস্ট)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=sys_instruction
        )
        
        # চ্যাট শুরু
        chat = model.start_chat(history=[])
        response = chat.send_message(request.message)
        
        return {"response": response.text}

    except Exception as e:
        # ⚠️ যদি এরর হয়, আমরা চেক করব কেন হলো
        error_msg = str(e)
        
        if "404" in error_msg or "not found" in error_msg.lower():
            # 🚑 DIAGNOSTIC MODE: সার্ভারে কী কী মডেল আছে তা খুঁজে বের করা
            try:
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
                
                # ইউজারকে মডেলের লিস্ট পাঠানো
                return {
                    "response": f"দাদুর ব্রেন কানেকশনে সমস্যা হচ্ছে। সার্ভারে এভেলেবল মডেলগুলো হলো: {available_models}। দয়া করে ডেভেলপারকে এই লিস্টটি দেখান।"
                }
            except Exception as list_error:
                 return {"response": f"Model Error: {error_msg}. (List Error: {list_error})"}
        
        return {"response": f"Server Error: {error_msg}"}

@app.get("/")
def home():
    return {"status": "Math Dadu Diagnostic Mode Running"}
