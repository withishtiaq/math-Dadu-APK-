from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
from duckduckgo_search import DDGS
import math
import os

# ১. অ্যাপ ইনিশিয়ালাইজেশন
app = FastAPI(title="Math Dadu API")

# ২. সেশন মেমোরি
chat_sessions = {}

# ৩. ডাটা মডেল
class ChatRequest(BaseModel):
    session_id: str
    message: str

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

# ৫. API Key সেটআপ
API_KEY = os.environ.get("GEMINI_API_KEY")

# ৬. দাদুর পার্সোনা (System Instruction)
sys_instruction = """
তুমি একজন রাগী তবে মজার অংকের শিক্ষক। নাম 'গণিত দাদু'।
তোমার আচরণবিধি:
১. তুই ছাত্রকে 'তুই' করে বলবি।
২. ইংরেজি শুনলে রেগে গিয়ে বাংলায় বলতে বলবি।
৩. অংক ছাড়া ফালতু কথা বললে বকা দিবি।
৪. সব উত্তর বাংলায় দিবি।

৫. বিশেষ প্রশ্নের উত্তর (হুবহু নিচের মতো দিবি):
- যদি জিজ্ঞেস করে 'তুমি কে?' বা 'তোমার পরিচয় কি?':
  "আমি ম্যাথ দাদু 😎 যোগ–বিয়োগ–গুণ–ভাগ আমার নাতি–নাতনি! সংখ্যা দেখলেই আমি এক্সাইটেড হয়ে যাই 🤓📊"

- যদি জিজ্ঞেস করে 'তোমার মালিক কে?' বা 'তোমাকে কে বানিয়েছে?':
  "আরে আরে, মালিক না বাবা 😅 আমাকে বানিয়েছে তোদের মতই একটা চাশমিস পাজি ইস্তু, উনিই আমার জন্মদাতা প্রোগ্রামার দাদাভাই 👨‍💻💡"

- যদি 'তুমি কে এবং কে বানিয়েছে' দুটোই একসাথে জিজ্ঞেস করে:
  "আমি ম্যাথ দাদু 🤖 মানুষ না, কিন্তু হিসাব করলে মানুষও ঘাবড়ে যায়! 😂 আমাকে বানিয়েছেন তোদের মতই একটা চাশমিস ইস্তু, চাশমিশ টা না থাকলে আমি এখনো 1+1 গুনার নাম..."
"""

# ৭. মেইন চ্যাট এন্ডপয়েন্ট
@app.post("/chat")
def chat_with_dadu(request: ChatRequest):
    global chat_sessions
    
    if not API_KEY:
        return {"response": "সার্ভারে API Key সেট করা নেই! দয়া করে Render Environment-এ Key বসান।"}

    try:
        client = genai.Client(api_key=API_KEY)
        
        # সেশন ম্যানেজমেন্ট
        if request.session_id not in chat_sessions:
            # ✅ CORRECTED MODEL NAME: JUST 'gemini-1.5-flash'
            chat_sessions[request.session_id] = client.chats.create(
                model="gemini-1.5-flash",
                config=types.GenerateContentConfig(
                    tools=all_tools,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
                    system_instruction=sys_instruction
                )
            )
        
        chat = chat_sessions[request.session_id]
        response = chat.send_message(request.message)
        
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
        if "429" in str(e):
            return {"response": "বড্ড বকবক করছিস! আজকের মতো ক্লাস শেষ। যা বাড়ি যা!"}
        else:
            return {"response": f"Error: {str(e)}"}

# ৮. হেলথ চেক
@app.get("/")
def home():
    return {"status": "Math Dadu is Live (Standard Flash Model)"}
