from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from duckduckgo_search import DDGS
import math
import os

app = FastAPI(title="Math Dadu API")
chat_sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

def web_search(query: str):
    try:
        results = DDGS().text(query, max_results=2)
        return str(results) if results else "No results found."
    except Exception as e:
        return f"Error: {e}"

# Math tools
def add_numbers(a: float, b: float) -> float: return a + b
def subtract_numbers(a: float, b: float) -> float: return a - b
def multiply_numbers(a: float, b: float) -> float: return a * b
def divide_numbers(a: float, b: float) -> float: return "Error" if b == 0 else a / b
def power_numbers(base: float, exponent: float) -> float: return math.pow(base, exponent)
def sqrt_number(x: float) -> float: return math.sqrt(x)
def factorial_number(n: int) -> int:
    try: return math.factorial(int(n))
    except: return "Error"

tools_list = [web_search, add_numbers, subtract_numbers, multiply_numbers, divide_numbers, power_numbers, sqrt_number, factorial_number]

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

sys_instruction = """
তুমি একজন রাগী তবে মজার অংকের শিক্ষক। নাম 'গণিত দাদু'।
তোমার আচরণবিধি:
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
    global chat_sessions
    if not API_KEY:
        return {"response": "API Key Missing!"}

    try:
        if request.session_id not in chat_sessions:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash", tools=tools_list, system_instruction=sys_instruction)
            chat_sessions[request.session_id] = model.start_chat(history=[])
        
        chat = chat_sessions[request.session_id]
        response = chat.send_message(request.message)
        
        full_response = response.text if response.text else "(হিসাব শেষ।)"
        return {"response": full_response}

    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@app.get("/")
def home():
    return {"status": "Math Dadu Live (Stable)"}
