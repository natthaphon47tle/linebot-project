from flask import Flask, request
import os
import gspread

from dotenv import load_dotenv
import os
from google.oauth2.service_account import Credentials

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage
)

# =========================
# LOAD ENV
# =========================

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# =========================
# FLASK
# =========================

app = Flask(__name__)

# =========================
# LINE API
# =========================

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# =========================
# GOOGLE SHEET
# =========================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "line-bot-496709-f358902967e6.json",
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("LineBotUsers").sheet1
tracking_sheet = client.open("LineBotUsers").worksheet("tracking")
faq_sheet = client.open("LineBotUsers").worksheet("faq")

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
# MESSAGE EVENT
# =========================

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_id = event.source.user_id
    text = event.message.text.strip()

    # =========================
    # LOGIN
    # =========================

    if text.startswith("login"):

        try:

            _, username, password = text.split()

            records = sheet.get_all_records()

            found = False

            for row in records:

                if (
                    row["username"] == username and
                    str(row["password"]) == password
                ):

                    found = True
                    break

            if found:

                if user_id not in logged_in_users:
                    logged_in_users.append(user_id)

                reply = "✅ Login สำเร็จ"

            else:
                reply = "❌ Username หรือ Password ไม่ถูกต้อง"

        except:
            reply = "ใช้รูปแบบ:\nlogin username password"

    # =========================
    # LOGOUT
    # =========================

    elif text.lower() == "logout":

        if user_id in logged_in_users:
            logged_in_users.remove(user_id)

        reply = "✅ Logout สำเร็จ"

    # =========================
    # NOT LOGIN
    # =========================

    elif user_id not in logged_in_users:

        reply = "กรุณา Login ก่อนใช้งาน"

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
                "1. service\n"
                "2. contact\n"
                "3. warehouse\n"
                "4. transport\n"
                "5. customs\n"
                "6. tracking <เลข>"
            )

        # =========================
        # SERVICE
        # =========================

        elif text.lower() == "service":

            reply = (
                "🚚 SERVICES\n\n"
                "- Freight Forwarder\n"
                "- Customs Clearance\n"
                "- Truck Transport\n"
                "- Warehouse\n"
                "- Cross Border\n"
                "- Cargo Insurance"
            )

        # =========================
        # CONTACT
        # =========================

        elif text.lower() == "contact":

            reply = (
                "📞 CONTACT\n\n"
                "Tel : 02-xxx-xxxx\n"
                "Email : test@company.com"
            )

        # =========================
        # WAREHOUSE
        # =========================

        elif text.lower() == "warehouse":

            reply = (
                "🏢 Warehouse Service\n\n"
                "- Storage\n"
                "- Inventory\n"
                "- Distribution"
            )

        # =========================
        # TRANSPORT
        # =========================

        elif text.lower() == "transport":

            reply = (
                "🚛 Transport Service\n\n"
                "- Domestic\n"
                "- Cross Border\n"
                "- Reefer Truck"
            )

        # =========================
        # CUSTOMS
        # =========================

        elif text.lower() == "customs":

            reply = (
                "📄 Customs Clearance\n\n"
                "- Import\n"
                "- Export\n"
                "- Documentation"
            )

        # =========================
        # TRACKING
        # =========================

        elif text.lower().startswith("tracking"):

            parts = text.split()

            if len(parts) < 2:

                reply = "กรุณาระบุเลข Tracking"

            else:

                tracking_number = parts[1]

                records = tracking_sheet.get_all_records()

                found = False

                for row in records:

                    if row["tracking"] == tracking_number:

                        found = True

                        flex_message = FlexSendMessage(
                            alt_text="Tracking Status",
                            contents={
                                "type": "bubble",
                                "body": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [

                                        {
                                            "type": "text",
                                            "text": "📦 Tracking Status",
                                            "weight": "bold",
                                            "size": "xl"
                                        },

                                        {
                                            "type": "separator",
                                            "margin": "md"
                                        },

                                        {
                                            "type": "text",
                                            "text": f"Tracking : {row['tracking']}",
                                            "margin": "md"
                                        },

                                        {
                                            "type": "text",
                                            "text": f"Status : {row['status']}"
                                        },

                                        {
                                            "type": "text",
                                            "text": f"Location : {row['location']}"
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

                if not found:
                    reply = "❌ ไม่พบ Tracking นี้"

        # =========================
        # FAQ
        # =========================

        else:

            records = faq_sheet.get_all_records()

            found = False

            for row in records:

                if row["keyword"].lower() == text.lower():

                    reply = row["answer"]

                    found = True
                    break

            if not found:

                reply = (
                    "❌ ไม่พบข้อมูล\n\n"
                    "พิมพ์ menu เพื่อดูเมนู"
                )

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