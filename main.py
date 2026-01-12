from flask import Flask, request, jsonify
import os
from google import genai
from google.genai import types
from duckduckgo_search import DDGS
import math

app = Flask(__name__)

# --- ১. টুলস (Tools) ---
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

# টুলস লিস্ট
all_tools = [web_search, add_numbers, subtract_numbers, multiply_numbers, divide_numbers, power_numbers, sqrt_number, factorial_number]

# --- ২. দাদুর পার্সোনা (System Instruction) ---
sys_instruction = """
তুমি একজন রাগী অংকের শিক্ষক। নাম 'গণিত দাদু'।
১. তুই ছাত্রকে 'তুই' করে বলবি।
২. ইংরেজি শুনলে রেগে গিয়ে বাংলায় বলতে বলবি।
৩. অংক ছাড়া ফালতু কথা বললে বকা দিবি।
৪. সব উত্তর বাংলায় দিবি।
"""

@app.route('/', methods=['GET'])
def home():
    return "গণিত দাদু সার্ভার রানিং! (Use POST /chat)"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # ১. FlutterFlow থেকে ডাটা নেওয়া
        data = request.get_json()
        user_input = data.get('userQuery')
        
        if not user_input:
            return jsonify({"response": "কিরে? কিছু তো বলবি নাকি?"}), 400

        # ২. API Key নেওয়া (Render Environment থেকে)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"response": "সার্ভারে API Key সেট করা নেই!"}), 500

        # ৩. ক্লায়েন্ট ইনিশিয়ালাইজ করা (প্রতি রিকোয়েস্টে নতুন করে)
        client = genai.Client(api_key=api_key)

        # ৪. চ্যাট তৈরি এবং মেসেজ পাঠানো
        # model="gemini-1.5-flash" ব্যবহার করছি কারণ এটি দ্রুত এবং স্টবল
        chat = client.chats.create(
            model="gemini-1.5-flash", 
            config=types.GenerateContentConfig(
                tools=all_tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
                system_instruction=sys_instruction
            )
        )

        response = chat.send_message(user_input)

        # ৫. উত্তর পাঠানো
        final_response = response.text if response.text else "(হিসাব শেষ।)"
        return jsonify({"response": final_response})

    except Exception as e:
        return jsonify({"response": f"দাদুর মাথা গরম হয়ে গেছে (Error): {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
