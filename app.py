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

conn = sqlite3.connect("database.db", check_same_thread=False)
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

# FAQ
cursor.execute("SELECT * FROM faq")

if not cursor.fetchall():

    cursor.execute("""
    INSERT INTO faq VALUES
    ('customs', 'บริการด้านพิธีการศุลกากร Import / Export'),
    ('warehouse', 'บริการคลังสินค้าและกระจายสินค้า')
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

logged_in_users = []
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

<button onclick="login()">
Login
</button>

<p id="msg"></p>

</div>

<script>

async function login() {

    const username =
    document.getElementById("username").value;

    const password =
    document.getElementById("password").value;

    const response = await fetch("/save_user", {

    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({
        user_id: profile.userId
    })

});

console.log(await response.text());

alert("✅ Login Success");

liff.closeWindow();

    const result = await response.text();

    if (result !== "SUCCESS") {

        document.getElementById("msg").innerHTML =
        "❌ Username หรือ Password ไม่ถูกต้อง";

        return;
    }

    await liff.init({

        liffId: "2010145479-TA2Uw8Ik",

        withLoginOnExternalBrowser: true

    });

    if (!liff.isLoggedIn()) {

        liff.login();

        return;
    }

    const profile = await liff.getProfile();

    await fetch("/save_user", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            user_id: profile.userId
        })

    });

    liff.closeWindow();

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

    data = request.json

    username = data["username"]
    password = data["password"]

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

    print("SAVE USER:", user_id)

    if user_id not in logged_in_users:

        logged_in_users.append(user_id)

    print("ALL LOGIN USERS:", logged_in_users)

    return "OK"


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

                            "uri": "https://liff.line.me/2010145479-TA2Uw8Ik"

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
    print("LOGIN USERS:", logged_in_users)

    # =========================
    # LOGOUT
    # =========================

    if text.lower() == "logout":

        if user_id in logged_in_users:
            logged_in_users.remove(user_id)

        reply = "✅ Logout สำเร็จ"

    # =========================
    # NOT LOGIN
    # =========================

    elif user_id not in logged_in_users:

        profile = line_bot_api.get_profile(
            event.source.user_id
        )

        display_name = profile.display_name

        flex_message = FlexSendMessage(

            alt_text="Login",

            contents={

                "type": "bubble",

                "hero": {

                    "type": "image",

                    "url": "https://drive.google.com/uc?export=view&id=1oZw_jQDf_pRRBaD-h04uEEOI1wXP0AF9",

                    "size": "sm",

                    "aspectRatio": "1:1",

                    "aspectMode": "fit"

                },

                "body": {

                    "type": "box",

                    "layout": "vertical",

                    "contents": [

                        {

                            "type": "text",

                            "text": f"สวัสดีคุณ {display_name}",

                            "weight": "bold",

                            "size": "lg"

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

                                "uri": "https://liff.line.me/2010145479-TA2Uw8Ik"

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

        return

    # =========================
    # LOGIN SUCCESS
    # =========================

    else:

        # =========================
        # MENU
        # =========================

        if text.lower() == "menu":

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
        # TRUCKING
        # =========================

        elif "trucking" in text.lower():

            try:

                df = pd.read_excel(
                    "tracking_reefer.xlsx"
                )

                result = ""

                for index, row in df.iterrows():

                    result += (
                        f"🚛 บริษัท: {row['company']}\n"
                        f"👤 ชื่อ: {row['contact']}\n"
                        f"📧 Email: {row['email']}\n"
                        f"📞 Tel: {row['tel']}\n"
                        f"📍 Base: {row['Base']}\n\n"
                    )

                reply = result

            except Exception as e:

                reply = f"❌ Trucking Error\n\n{str(e)}"

        # =========================
        # CUSTOMS
        # =========================

        elif "customs" in text.lower():

            try:

                df = pd.read_excel(
                    "customs_clearance.xlsx"
                )

                result = ""

                for index, row in df.iterrows():

                    result += (
                        f"📄 บริษัท: {row['company']}\n"
                        f"👤 ชื่อ: {row['contact']}\n"
                        f"📧 Email: {row['email']}\n"
                        f"📞 Tel: {row['tel']}\n"
                        f"📍 Base: {row['base']}\n\n"
                    )

                reply = result

            except Exception as e:

                reply = f"❌ Customs Error\n\n{str(e)}"

        # =========================
        # INSURANCE
        # =========================

        elif "insurance" in text.lower():

            try:

                df = pd.read_excel(
                    "cargo_insurance.xlsx"
                )

                result = ""

                for index, row in df.iterrows():

                    result += (
                        f"🛡 บริษัท: {row['company']}\n"
                        f"👤 ชื่อ: {row['contact']}\n"
                        f"📧 Email: {row['email']}\n"
                        f"📞 Tel: {row['tel']}\n\n"
                    )

                reply = result

            except Exception as e:

                reply = f"❌ Insurance Error\n\n{str(e)}"

        # =========================
        # PACKING
        # =========================

        elif "packing" in text.lower():

            try:

                df = pd.read_excel(
                    "packing.xlsx"
                )

                result = ""

                for index, row in df.iterrows():

                    result += (
                        f"📦 บริษัท: {row['company']}\n"
                        f"👤 ชื่อ: {row['contact']}\n"
                        f"📧 Email: {row['email']}\n"
                        f"📞 Tel: {row['tel']}\n"
                        f"🛠 Service: {row['Service']}\n"
                        f"📍 Base: {row['Base']}\n\n"
                    )

                reply = result

            except Exception as e:

                reply = f"❌ Packing Error\n\n{str(e)}"

        # =========================
        # CROSS BORDER
        # =========================

        elif "cross" in text.lower():

            try:

                df = pd.read_excel(
                    "cross_border.xlsx"
                )

                result = ""

                for index, row in df.iterrows():

                    result += (
                        f"🌏 บริษัท: {row['company']}\n"
                        f"👤 ชื่อ: {row['contact']}\n"
                        f"📧 Email: {row['email']}\n"
                        f"📞 Tel: {row['tel']}\n"
                        f"🛣 Route: {row['Route']}\n\n"
                    )

                reply = result

            except Exception as e:

                reply = f"❌ Cross Border Error\n\n{str(e)}"

        # =========================
        # COURIER
        # =========================

        elif "courier" in text.lower():

            try:

                df = pd.read_excel(
                    "courier.xlsx"
                )

                result = ""

                for index, row in df.iterrows():

                    result += (
                        f"📮 บริษัท: {row['company']}\n"
                        f"👤 ชื่อ: {row['contact']}\n"
                        f"📧 Email: {row['email']}\n"
                        f"📞 Tel: {row['tel']}\n\n"
                    )

                reply = result

            except Exception as e:

                reply = f"❌ Courier Error\n\n{str(e)}"

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