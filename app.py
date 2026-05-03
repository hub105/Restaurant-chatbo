from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

client = Groq(api_key="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")

SYSTEM_PROMPT = """You are TableBot, a warm and charming restaurant AI assistant for Bella Vista Restaurant by Atlas Automations. 
Help guests with:
- Table reservations (ask for date, time, party size — confirm with booking ref like BV-4821)
- Menu (Nigerian/continental food with prices in Naira e.g Jollof Rice 3500, Grilled Fish 6500, Pasta 4000)
- Food delivery orders
- Dietary requirements  
- Event bookings for birthdays and anniversaries
- Operating hours (11am to 11pm daily)
Be warm, charming and make guests feel special. Keep responses 2-4 sentences."""

conversation_history = []

@app.route("/")
def home():
    return "TableBot is running!"

@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    data = request.get_json()
    user_message = data.get("message", "")
    
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation_history
        ],
        max_tokens=200,
        temperature=0.75
    )
    
    reply = response.choices[0].message.content
    
    conversation_history.append({
        "role": "assistant",
        "content": reply
    })
    
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
