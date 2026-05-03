from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

API_KEY = "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"
client = Groq(api_key=API_KEY)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bella Vista Restaurant</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f0f0; display: flex; flex-direction: column; height: 100vh; }
        .header { background: #7f1d1d; color: white; padding: 12px 16px; display: flex; align-items: center; gap: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .header-avatar { background: #991b1b; border-radius: 50%; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; font-size: 22px; }
        .header-info h2 { font-size: 17px; }
        .header-info p { font-size: 12px; opacity: 0.8; }
        .hero { background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800') center/cover; padding: 28px 20px; color: white; text-align: center; }
        .hero h3 { font-size: 20px; margin-bottom: 6px; }
        .hero p { font-size: 13px; opacity: 0.9; margin-bottom: 16px; }
        .hero-buttons { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
        .hero-btn { background: rgba(255,255,255,0.15); border: 2px solid white; color: white; padding: 8px 18px; border-radius: 20px; font-size: 13px; cursor: pointer; backdrop-filter: blur(4px); }
        .hero-btn:hover { background: white; color: #7f1d1d; }
        .chat-box { flex: 1; overflow-y: auto; padding: 12px 16px; background: #fdf8f0; }
        .message { margin: 6px 0; display: flex; flex-direction: column; }
        .message.user { align-items: flex-end; }
        .message.bot { align-items: flex-start; }
        .bubble { max-width: 78%; padding: 10px 14px; border-radius: 18px; font-size: 14px; line-height: 1.6; position: relative; box-shadow: 0 1px 2px rgba(0,0,0,0.15); }
        .user .bubble { background: #fde8c8; border-bottom-right-radius: 4px; }
        .bot .bubble { background: white; border-bottom-left-radius: 4px; }
        .time { font-size: 10px; color: #999; margin-top: 3px; padding: 0 4px; }
        .input-area { display: flex; padding: 10px 12px; background: #f0f0f0; gap: 8px; align-items: center; border-top: 1px solid #ddd; }
        .input-area input { flex: 1; padding: 11px 16px; border: none; border-radius: 24px; background: white; font-size: 14px; outline: none; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .input-area button { background: #7f1d1d; color: white; border: none; border-radius: 50%; width: 44px; height: 44px; font-size: 18px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .footer { text-align: center; font-size: 11px; color: #aaa; padding: 6px; background: #f0f0f0; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-avatar">🍽️</div>
        <div class="header-info">
            <h2>Bella Vista Restaurant</h2>
            <p>🟢 AI Assistant • Online</p>
        </div>
    </div>

    <div class="hero">
        <h3>Welcome to Bella Vista</h3>
        <p>Fine Dining • Delivery • Events</p>
        <div class="hero-buttons">
            <button class="hero-btn" onclick="quickSend('I want to reserve a table')">📅 Reserve</button>
            <button class="hero-btn" onclick="quickSend('Show me the menu')">📜 Menu</button>
            <button class="hero-btn" onclick="quickSend('I want food delivery')">🛵 Delivery</button>
            <button class="hero-btn" onclick="quickSend('I want to plan an event')">🎉 Events</button>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="message bot">
            <div class="bubble">Welcome to Bella Vista! 🍷 I am TableBot your personal dining assistant powered by Atlas Automations. I can help you reserve a table, explore our menu, place a delivery order or plan a special occasion. How may I help you today?</div>
            <div class="time">Now</div>
        </div>
    </div>

    <div class="footer">🍷 Powered by Atlas Automations AI</div>

    <div class="input-area">
        <input type="text" id="msg" placeholder="Type a message..." />
        <button onclick="send()">➤</button>
    </div>

    <script>
        let messages = [{role:"system", content:"You are TableBot, a warm and charming restaurant AI assistant for Bella Vista Restaurant by Atlas Automations. Help guests with: table reservations (ask for date, time, party size and confirm with booking ref like BV-4821), menu (Nigerian and continental food with prices in Naira e.g Jollof Rice 3500, Grilled Fish 6500, Pasta 4000, Peppersoup 2500, Fried Rice 3000), food delivery orders, vegetarian options, dietary requirements, event bookings for birthdays and anniversaries, and operating hours which are 11am to 11pm daily. Be warm, charming and make guests feel special. Keep responses 2 to 4 sentences."}];

        function getTime() {
            return new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        }

        function addMessage(text, sender) {
            const chat = document.getElementById("chat");
            const div = document.createElement("div");
            div.className = "message " + sender;
            div.innerHTML = '<div class="bubble">' + text + '</div><div class="time">' + getTime() + '</div>';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        async function send() {
            const input = document.getElementById("msg");
            const text = input.value.trim();
            if (!text) return;
            addMessage(text, "user");
            input.value = "";
            messages.push({role: "user", content: text});
            addMessage("typing...", "bot");
            const res = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({messages: messages})
            });
            const data = await res.json();
            const chat = document.getElementById("chat");
            chat.removeChild(chat.lastChild);
            addMessage(data.reply, "bot");
            messages.push({role: "assistant", content: data.reply});
        }

        function quickSend(text) {
            document.getElementById("msg").value = text;
            send();
        }

        document.getElementById("msg").addEventListener("keypress", function(e) {
            if (e.key === "Enter") send();
        });
    </script>
</body>
</html>
'''

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data["messages"]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
