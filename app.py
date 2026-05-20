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

                            "uri": "https://linebot-project-0qio.onrender.com/login"

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

            reply = "🚛 Trucking Service"

        # =========================
        # CUSTOMS
        # =========================

        elif "customs" in text.lower():

            reply = "📄 Customs Clearance"

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