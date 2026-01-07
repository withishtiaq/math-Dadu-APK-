from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
from duckduckgo_search import DDGS
import math
import os

# ১. অ্যাপ ইনিশিয়ালাইজেশন
app = FastAPI(title="Math Dadu API")

# ২. সেশন মেমোরি (Temporary Memory)
# সার্ভার রিস্টার্ট হলে এটি মুছে যাবে, কিন্তু টেস্ট করার জন্য যথেষ্ট
chat_sessions = {}

# ৩. ডাটা মডেল (FlutterFlow থেকে যা আসবে)
class ChatRequest(BaseModel):
    session_id: str  # প্রতিটি ইউজারের আলাদা আইডি (যেমন: user_1, user_2)
    message: str     # ইউজারের প্রশ্ন

# ৪. টুলস (Tools)
def web_search(query: str):
    try:
        results = DDGS().text(query, max_results=2)
        return str(results) if results else "No results found."
    except Exception as e:
        return f"Error: {e}"

def add_numbers(a: float, b: float) -> float: return a + b
def subtract_numbers(a: float, b: float) -> float: return a - b
def multiply_numbers(a: float, b: float) -> float: return a * b
def divide_numbers(a: float, b: float) -> float: return "Error" if b == 0 else a / b
def power_numbers(base: float, exponent: float) -> float: return math.pow(base, exponent)
def sqrt_number(x: float) -> float: return math.sqrt(x)
def factorial_number(n: int) -> int:
    try: return math.factorial(int(n))
    except: return "Error"

all_tools = [web_search, add_numbers, subtract_numbers, multiply_numbers, divide_numbers, power_numbers, sqrt_number, factorial_number]

# ৫. API Key সেটআপ (Render Environment থেকে নেবে)
# যদি লোকালে টেস্ট করেন, নিচের লাইনে আপনার Key বসাতে পারেন, তবে Render-এ আমরা সিক্রেট ভেরিয়েবল ব্যবহার করব।
API_KEY = os.environ.get("GEMINI_API_KEY") 

# ৬. মেইন চ্যাট এন্ডপয়েন্ট (API Endpoint)
@app.post("/chat")
def chat_with_dadu(request: ChatRequest):
    global chat_sessions
    
    # API Key চেক
    if not API_KEY:
        return {"response": "সার্ভারে API Key সেট করা নেই! দয়া করে Render Environment-এ Key বসান।"}

    try:
        # ক্লায়েন্ট সেটআপ
        client = genai.Client(api_key=API_KEY)
        
        # নতুন সেশন তৈরি বা পুরানো সেশন লোড করা
        if request.session_id not in chat_sessions:
            sys_instruction = """
            তুমি একজন রাগী অংকের শিক্ষক। নাম 'গণিত দাদু'।
            ১. তুই ছাত্রকে 'তুই' করে বলবি।
            ২. ইংরেজি শুনলে রেগে গিয়ে বাংলায় বলতে বলবি।
            ৩. অংক ছাড়া ফালতু কথা বললে বকা দিবি।
            ৪. সব উত্তর বাংলায় দিবি।
            """
            
            chat_sessions[request.session_id] = client.chats.create(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(
                    tools=all_tools,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
                    system_instruction=sys_instruction
                )
            )
        
        # চ্যাট সেশন থেকে উত্তর বের করা
        chat = chat_sessions[request.session_id]
        response = chat.send_message(request.message)
        
        # টেক্সট এক্সট্রাকশন
        full_response = ""
        if response.text:
            full_response = response.text
        elif response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.text: full_response += part.text
        
        if not full_response:
            full_response = "(হিসাব শেষ।)"

        return {"response": full_response}

    except Exception as e:
        # লিমিট শেষ হলে দাদুর মেসেজ
        if "429" in str(e):
            return {"response": "বড্ড বকবক করছিস! আজকের মতো ক্লাস শেষ। যা বাড়ি যা!"}
        else:
            return {"response": f"Error: {str(e)}"}

# ৭. হেলথ চেক (সার্ভার ঠিক আছে কিনা দেখার জন্য)
@app.get("/")
def home():
    return {"status": "Math Dadu is Live on API!"}
