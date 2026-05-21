import os
from flask import Flask, request, render_template, redirect, session
import os

from dotenv import load_dotenv
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from openai import OpenAI

# =========================
# DATABASE
# =========================

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

conn.execute("PRAGMA journal_mode=WAL")

cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
""")

# TRACKING TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS tracking (
    tracking TEXT,
    status TEXT,
    location TEXT
)
""")

# FAQ TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS faq (
    keyword TEXT,
    answer TEXT
)
""")

conn.commit()

# =========================
# DEFAULT DATA
# =========================

# USERS
cursor.execute("SELECT * FROM users")

if not cursor.fetchall():

    cursor.execute("""
    INSERT INTO users VALUES
(
    'admin',
    '{}'
),
(
    'leo',
    '{}'
)
""".format(
    generate_password_hash('1234'),
    generate_password_hash('9999')
))
# TRACKING
cursor.execute("SELECT * FROM tracking")

if not cursor.fetchall():

    cursor.execute("""
    INSERT INTO tracking VALUES
    ('ABC123', 'In Transit', 'Bangkok'),
    ('XYZ999', 'Delivered', 'Laem Chabang')
    """)

# FAQ TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS faq (
    keyword TEXT,
    answer TEXT
)
""")

conn.commit()

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    FollowEvent
)

# =========================
# LOAD ENV
# =========================

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# =========================
# FLASK
# =========================

app = Flask(__name__)
app.secret_key = "bdvm_secret"

# =========================
# LINE API
# =========================

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# =========================
# LOGIN SESSION
# =========================

COMPANY_PASSWORD = "BDVM2026"

# =========================
# HOME
# =========================
@app.route("/")
def home():

    return "LINE BOT RUNNING"

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users")
        records = cursor.fetchall()

        for row in records:

            if (
                row[0] == username and
                check_password_hash(row[1], password)
            ):

                session["user"] = username

                return """
<h2>✅ Login Success</h2>
<p>กลับไปใช้งาน LINE BOT ได้เลย</p>
"""

    return render_template("login.html")


# =========================
# LIFF LOGIN
# =========================

@app.route("/liff")
def liff():

    return """
<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8">

<script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>

<style>

body{
    font-family:Arial;
    background:#f4f4f4;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}

.box{
    background:white;
    padding:30px;
    border-radius:20px;
    width:320px;
    text-align:center;
    box-shadow:0 0 10px rgba(0,0,0,0.1);
}

input{
    width:100%;
    padding:12px;
    margin-top:15px;
    border-radius:10px;
    border:1px solid #ccc;
}

button{
    width:100%;
    padding:12px;
    margin-top:20px;
    background:#06C755;
    color:white;
    border:none;
    border-radius:10px;
    font-size:16px;
}

</style>

</head>

<body>

<div class="box">

<h2>🔐 BDVM LOGIN</h2>

<input
    type="text"
    id="username"
    placeholder="Username"
>

<input
    type="password"
    id="password"
    placeholder="Password"
>

<button
    type="button"
    onclick="login()"
>
Login
</button>

<p id="msg"></p>

</div>

<script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>

<script>

async function login() {

    alert("LOGIN BUTTON CLICKED");

    try {

        await liff.init({
            liffId: "2010152202-xzzmHkWl"
        });

        alert("LIFF INIT SUCCESS");

        if (!liff.isLoggedIn()) {

            liff.login();

            return;
        }

        const username =
        document.getElementById("username").value;

        const password =
        document.getElementById("password").value;

        alert("START CHECK LOGIN");
        const response = await fetch("/check_login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username: username,
                password: password
            })

        });

        const result = await response.text();

        alert(result);

        if (result !== "SUCCESS") {

            document.getElementById("msg").innerHTML =
            "❌ Username หรือ Password ไม่ถูกต้อง";

            return;
        }

        document.getElementById("msg").innerHTML =
        "✅ LOGIN SUCCESS";
        
        await liff.init({
            liffId: "2010152202-xzzmHkWl"
        });

        const urlParams =
        new URLSearchParams(window.location.search);

        const lineUserId =
        urlParams.get("user_id");
        await fetch("/save_user", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                user_id: lineUserId
            })
    });

        document.getElementById("msg").innerHTML =
        "✅ LOGIN SUCCESS<br><br>กรุณากด X มุมขวาบนเพื่อกลับไปหน้าแชท";

    }

    catch(err) {

        alert(err);

    }

}

</script>

</body>

</html>
"""


# =========================
# CHECK LOGIN
# =========================

@app.route("/check_login", methods=["POST"])
def check_login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    cursor.execute("SELECT * FROM users")

    records = cursor.fetchall()

    for row in records:

        if (
            row[0] == username and
            check_password_hash(row[1], password)
        ):

            return "SUCCESS"

    return "FAIL"

# =========================
# SAVE USER
# =========================

@app.route("/save_user", methods=["POST"])
def save_user():

    data = request.get_json()

    user_id = data.get("user_id")

    users = []

    if os.path.exists("sessions.txt"):

        with open("sessions.txt", "r") as f:

            users = [u.strip() for u in f.readlines()]

    if user_id not in users:

        with open("sessions.txt", "r") as f:

            users = [u.strip() for u in f.readlines()]

    print("ALL USERS:", users)

    if user_id in users:

        logged_in = True

# =========================
# WEBHOOK
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():

    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)

    except InvalidSignatureError:
        return "Invalid Signature"

    return "OK"

# =========================
# FOLLOW EVENT
# =========================

@handler.add(FollowEvent)
def handle_follow(event):

    profile = line_bot_api.get_profile(
        event.source.user_id
    )

    display_name = profile.display_name

    flex_message = FlexSendMessage(

        alt_text="Login",

        contents={

            "type": "bubble",

            "body": {

                "type": "box",

                "layout": "vertical",

                "contents": [

                    {

                        "type": "text",

                        "text": f"สวัสดีคุณ {display_name}",

                        "weight": "bold",

                        "size": "xl"

                    },

                    {

                        "type": "text",

                        "text": "กรุณากดปุ่ม Login ด้านล่างก่อนใช้งาน",

                        "wrap": True,

                        "margin": "md"

                    }

                ]

            },

            "footer": {

                "type": "box",

                "layout": "vertical",

                "contents": [

                    {

                        "type": "button",

                        "style": "primary",

                        "action": {

                            "type": "uri",

                            "label": "Login",

                            "uri": f"https://liff.line.me/2010152202-xzzmHkWl?user_id={event.source.user_id}"

                        }

                    }

                ]

            }

        }

    )

    line_bot_api.reply_message(
        event.reply_token,
        flex_message
    )


# =========================
# MESSAGE EVENT
# =========================

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_id = event.source.user_id
    text = event.message.text.strip()

    print("CURRENT USER:", user_id)

    print("CURRENT USER:", user_id)

    logged_in = False

    if os.path.exists("sessions.txt"):

        with open("sessions.txt", "r") as f:

            users = f.read().splitlines()

            print("ALL USERS:", users)

            if user_id in users:

                logged_in = True

    print("LOGIN STATUS:", logged_in)
        if not logged_in:

        reply = (
            "🔐 กรุณา Login ก่อนใช้งาน\n\n"
            f"https://linebot-project-0qio.onrender.com/liff?user_id={user_id}"
        )

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

        return

    # =========================
    # LOGOUT
    # =========================

    if text.lower() == "logout":

        users = []

        if os.path.exists("sessions.txt"):

            with open("sessions.txt", "r") as f:

                users = [u.strip() for u in f.readlines()]

        users = [u for u in users if u != user_id]

        with open("sessions.txt", "w") as f:

            for u in users:

                f.write(u + "\\n")

        reply = "✅ Logout สำเร็จ"

    # =========================
    # MENU
    # =========================

    elif text.lower() == "menu":

        reply = (
            "📋 MENU\\n\\n"
            "1. trucking\\n"
            "2. customs\\n"
            "3. insurance\\n"
            "4. packing\\n"
            "5. cross border\\n"
            "6. courier"
        )

    # =========================
    # DEFAULT
    # =========================

    else:

        reply = "พิมพ์ menu เพื่อดูเมนู"

    # =========================
    # REPLY
    # =========================

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

           # =========================
    # LOGOUT
    # =========================

    with open("sessions.txt", "r") as f:

        users = [u.strip() for u in f.readlines()]

    # =========================
    # MENU
    # =========================

    elif text.lower() == "menu":

        reply = (
            "📋 MENU\n\n"
            "1. trucking\n"
            "2. customs\n"
            "3. insurance\n"
            "4. packing\n"
            "5. cross border\n"
            "6. courier"
        )

    # =========================
    # DEFAULT
    # =========================

    else:

        reply = "พิมพ์ menu เพื่อดูเมนู"

    # =========================
    # REPLY
    # =========================

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)