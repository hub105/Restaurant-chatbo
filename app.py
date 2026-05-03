from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

client = Groq(api_key="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")

SYSTEM_PROMPT = """You are TableBot, a warm and charming restaurant AI assistant for Bella Vista Restaurant by Atlas Automations. Help guests with table reservations (ask for date, time, party size, confirm with booking ref like BV-4821), menu (Nigerian/continental food with prices in Naira e.g Jollof Rice 3500, Grilled Fish 6500, Pasta 4000), food delivery orders, dietary requirements, event bookings for birthdays and anniversaries, and operating hours (11am to 11pm daily). Be warm and charming. Keep responses 2-4 sentences."""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TableBot - Atlas Automations</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#fdf8f0;font-family:'DM Sans',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:16px}
.wrap{width:100%;max-width:460px}
.top{display:flex;align-items:center;gap:12px;margin-bottom:18px}
.icon{width:50px;height:50px;background:linear-gradient(135deg,#b45309,#d97706);border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:24px}
.title h1{font-size:22px;font-weight:800;color:#1c0f00}
.title p{font-size:11px;color:#92400e;font-weight:600;letter-spacing:.5px;text-transform:uppercase}
.opn{margin-left:auto;font-size:10px;font-weight:700;color:#fff;background:linear-gradient(135deg,#dc2626,#ef4444);padding:5px 11px;border-radius:20px}
.card{background:#fff;border-radius:22px;overflow:hidden;box-shadow:0 16px 50px rgba(180,83,9,.1);border:1px solid #fde8c8}
.msgs{height:370px;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:13px;scroll-behavior:smooth}
.msg{display:flex;gap:9px;align-items:flex-end}
.msg.user{flex-direction:row-reverse}
.av{width:30px;height:30px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.av-b{background:linear-gradient(135deg,#b45309,#d97706)}
.av-u{background:linear-gradient(135deg,#0891b2,#38bdf8)}
.bubble{max-width:80%;padding:11px 15px;font-size:13.5px;line-height:1.65}
.bot .bubble{background:#fff8ee;border:1px solid #fde8c8;border-radius:16px;border-bottom-left-radius:4px;color:#1c0f00}
.user .bubble{background:linear-gradient(135deg,#b45309,#d97706);color:#fff;border-radius:16px;border-bottom-right-radius:4px}
.typing{display:flex;gap:5px;align-items:center;padding:2px 0}
.typing span{width:7px;height:7px;background:#b45309;border-radius:50%;animation:jump .7s infinite}
.typing span:nth-child(2){animation-delay:.15s}.typing span:nth-child(3){animation-delay:.3s}
@keyframes jump{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}
.btns{padding:12px 18px;display:flex;flex-wrap:wrap;gap:7px;border-top:1px solid #fde8c8;background:#fff8ee}
.mb{background:#fff;border:1.5px solid #fde8c8;color:#92400e;padding:6px 12px;border-radius:20px;font-size:11.5px;cursor:pointer;font-weight:500;font-family:'DM Sans',sans-serif}
.mb:hover{border-color:#b45309;color:#b45309}
.inp-row{padding:14px 16px;border-top:1px solid #fde8c8;display:flex;gap:9px;align-items:center}
.inp-row input{flex:1;border:1.5px solid #fde8c8;border-radius:14px;padding:11px 15px;font-family:'DM Sans',sans-serif;font-size:13.5px;outline:none;background:#fff8ee;color:#1c0f00}
.inp-row input:focus{border-color:#b45309;background:#fff}
.inp-row input::placeholder{color:#e9b97a}
.sbtn{width:42px;height:42px;background:linear-gradient(135deg,#b45309,#d97706);border:none;border-radius:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.sbtn svg{width:15px;height:15px;fill:#fff}
.footer{text-align:center;margin-top:13px;font-size:11px;color:#d4a46a;font-weight:500}
.footer b{color:#b45309}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <div class="icon">🍽️</div>
    <div class="title"><h1>TableBot</h1><p>Restaurant AI · Atlas Automations</p></div>
    <div class="opn">🍴 Open</div>
  </div>
  <div class="card">
    <div class="msgs" id="msgs"></div>
    <div class="btns">
      <button class="mb" onclick="q('I want to book a table')">📅 Reserve</button>
      <button class="mb" onclick="q('Show me the menu')">📜 Menu</button>
      <button class="mb" onclick="q('Order food for delivery')">🛵 Delivery</button>
      <button class="mb" onclick="q('Vegetarian options')">🥗 Veggie</button>
      <button class="mb" onclick="q('Plan a birthday dinner')">🎉 Events</button>
    </div>
    <div class="inp-row">
      <input id="inp" placeholder="Reserve a table, view menu, order food…" onkeydown="if(event.key==='Enter')send()">
      <button class="sbtn" onclick="send()"><svg viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg></button>
    </div>
  </div>
  <div class="footer">Powered by <b>Atlas Automations</b> 🍷</div>
</div>
<script>
function addMsg(t,w){
  const m=document.getElementById('msgs');
  const d=document.createElement('div');d.className='msg '+w;
  d.innerHTML='<div class="av '+(w==='bot'?'av-b':'av-u')+'">'+(w==='bot'?'🍽️':'👤')+'</div><div class="bubble">'+t.replace(/\\n/g,'<br>')+'</div>';
  m.appendChild(d);m.scrollTop=m.scrollHeight;
}
function showTyping(){
  const m=document.getElementById('msgs');const d=document.createElement('div');
  d.className='msg bot';d.id='typ';
  d.innerHTML='<div class="av av-b">🍽️</div><div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
  m.appendChild(d);m.scrollTop=m.scrollHeight;
}
function hideTyping(){const t=document.getElementById('typ');if(t)t.remove();}
async function send(){
  const inp=document.getElementById('inp');const t=inp.value.trim();if(!t)return;inp.value='';
  addMsg(t,'user');showTyping();
  try{
    const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
    const d=await r.json();hideTyping();
    addMsg(d.reply||'Sorry please try again!','bot');
  }catch(e){hideTyping();addMsg('Something went wrong. Please try again!','bot');}
}
function q(t){document.getElementById('inp').value=t;send();}
setTimeout(()=>addMsg("Welcome to Bella Vista! 🍷 I am TableBot your personal dining assistant powered by Atlas Automations. I can help you reserve a table, explore our menu, place a delivery order or plan a special occasion. How may I help you today?","bot"),600);
</script>
</body>
</html>"""

conversation_history = []

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    data = request.get_json()
    user_message = data.get("message", "")
    conversation_history.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *conversation_history],
        max_tokens=200,
        temperature=0.75
    )
    reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
