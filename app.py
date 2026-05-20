from flask import Flask, request
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
    FlexSendMessage
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

            cursor.execute("SELECT * FROM users")
            records = cursor.fetchall()

            found = False

            for row in records:

                if (
                    row[0] == username and
                    check_password_hash(row[1], password)
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
                "6. tracking <เลข>\n"
                "7. trucking"
            )

        # =========================
        # TRUCKING & REEFER
        # =========================

        if "trucking" in text.lower():
            print(text)

            try:

                df = pd.read_excel("tracking_reefer.xlsx")

                reply = "🚛 Trucking & Reefer\n\n"

                for index, row in df.iterrows():

                    reply += (
                        f"Company : {row['company']}\n"
                        f"Contact : {row['contact']}\n"
                        f"Email : {row['email']}\n"
                        f"Tel : {row['tel']}\n"
                        f"Base : {row['Base']}\n\n"
                    )

            except Exception as e:

                reply = (
                    "❌ ไม่สามารถอ่านไฟล์ Excel ได้\n\n"
                    f"{str(e)}"
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

        elif "customs" in text.lower():

            try:

                df = pd.read_excel("customs_clearance.xlsx")

                reply = "📄 Customs Clearance\n\n"

                for index, row in df.iterrows():

                    reply += (
                        f"Company : {row['company']}\n"
                        f"Contact : {row['contact']}\n"
                        f"Email : {row['email']}\n"
                        f"Tel : {row['tel']}\n"
                        f"Base : {row['base']}\n\n"
                    )

            except Exception as e:

                reply = str(e)

        # =========================
        # INSURANCE
        # =========================

        elif "insurance" in text.lower():

            try:

                df = pd.read_excel("cargo_insurance.xlsx")

                reply = "🛡 Cargo Insurance\n\n"

                for index, row in df.iterrows():

                    reply += (
                        f"Company : {row['company']}\n"
                        f"Department : {row['department']}\n"
                        f"Contact : {row['contact']}\n"
                        f"Email : {row['email']}\n"
                        f"Tel : {row['tel']}\n"
                        f"Note : {row['note']}\n\n"
                    )

            except Exception as e:

                reply = str(e)

        # =========================
        # PACKING
        # =========================

        elif "packing" in text.lower():

            try:

                df = pd.read_excel("packing.xlsx")

                reply = "📦 Packing Service\n\n"

                for index, row in df.iterrows():

                    reply += (
                        f"Company : {row['company']}\n"
                        f"Contact : {row['contact']}\n"
                        f"Email : {row['email']}\n"
                        f"Tel : {row['tel']}\n"
                        f"Service : {row['service']}\n"
                        f"Base : {row['base']}\n\n"
                    )

            except Exception as e:

                reply = str(e)

        # =========================
        # CROSS BORDER
        # =========================

        elif (
            "cross border" in text.lower()
            or
            "crossborder" in text.lower()
        ):

            try:

                df = pd.read_excel("cross_border.xlsx")

                reply = "🌏 Cross Border\n\n"

                for index, row in df.iterrows():

                    reply += (
                        f"Company : {row['company']}\n"
                        f"Contact : {row['contact']}\n"
                        f"Email : {row['email']}\n"
                        f"Tel : {row['tel']}\n"
                        f"Route : {row['route']}\n\n"
                    )

            except Exception as e:

                reply = str(e)

        # =========================
        # COURIER
        # =========================

        elif "courier" in text.lower():

            try:

                df = pd.read_excel("courier.xlsx")

                reply = "📦 Courier Service\n\n"

                for index, row in df.iterrows():

                    reply += (
                        f"Company : {row['company']}\n"
                        f"Contact : {row['contact']}\n"
                        f"Email : {row['email']}\n"
                        f"Tel : {row['tel']}\n\n"
                    )

            except Exception as e:

                reply = str(e)

        # =========================
        # TRACKING
        # =========================

        elif text.lower().startswith("tracking "):

            parts = text.split()

            if len(parts) < 2:

                reply = "กรุณาระบุเลข Tracking"

            else:

                tracking_number = parts[1]

                cursor.execute("SELECT * FROM tracking")
                records = cursor.fetchall()

                found = False

                for row in records:

                    if row[0] == tracking_number:

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
                                            "text": f"Tracking : {row[0]}",
                                            "margin": "md"
                                        },

                                        {
                                            "type": "text",
                                            "text": f"Status : {row[1]}"
                                        },

                                        {
                                            "type": "text",
                                            "text": f"Location : {row[2]}"
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
        # AI SEARCH
        # =========================

        else:

            try:

                # LOAD ALL EXCEL

                trucking_df = pd.read_excel("tracking_reefer.xlsx")
                customs_df = pd.read_excel("customs_clearance.xlsx")
                insurance_df = pd.read_excel("cargo_insurance.xlsx")
                packing_df = pd.read_excel("packing.xlsx")
                cross_df = pd.read_excel("cross_border.xlsx")
                courier_df = pd.read_excel("courier.xlsx")

                # COMBINE DATA

                all_data = f"""
                TRUCKING:
                {trucking_df.to_string()}

                CUSTOMS:
                {customs_df.to_string()}

                INSURANCE:
                {insurance_df.to_string()}

                PACKING:
                {packing_df.to_string()}

                CROSS BORDER:
                {cross_df.to_string()}

                COURIER:
                {courier_df.to_string()}
                """

                # AI
                # SEARCH COMPANY

                filtered_data = ""

                company_name = text.replace("ข้อมูลบริษัท", "").strip()

                # TRUCKING

                trucking_match = trucking_df[
                    trucking_df["company"]
                    .str.contains(company_name, case=False, na=False)
                ]

                if not trucking_match.empty:

                    filtered_data += (
                        "\nTRUCKING:\n"
                        + trucking_match.to_string()
                    )

                # CUSTOMS

                customs_match = customs_df[
                    customs_df["company"]
                    .str.contains(company_name, case=False, na=False)
                ]

                if not customs_match.empty:

                    filtered_data += (
                        "\nCUSTOMS:\n"
                        + customs_match.to_string()
                    )

                # INSURANCE

                insurance_match = insurance_df[
                    insurance_df["company"]
                    .str.contains(company_name, case=False, na=False)
                ]

                if not insurance_match.empty:

                    filtered_data += (
                        "\nINSURANCE:\n"
                        + insurance_match.to_string()
                    )

                # PACKING

                packing_match = packing_df[
                    packing_df["company"]
                    .str.contains(company_name, case=False, na=False)
                ]

                if not packing_match.empty:

                    filtered_data += (
                        "\nPACKING:\n"
                        + packing_match.to_string()
                    )

                # CROSS BORDER

                cross_match = cross_df[
                    cross_df["company"]
                    .str.contains(company_name, case=False, na=False)
                ]

                if not cross_match.empty:

                    filtered_data += (
                        "\nCROSS BORDER:\n"
                        + cross_match.to_string()
                    )

                # COURIER

                courier_match = courier_df[
                    courier_df["company"]
                    .str.contains(company_name, case=False, na=False)
                ]

                if not courier_match.empty:

                    filtered_data += (
                        "\nCOURIER:\n"
                        + courier_match.to_string()
                    )

                response = client.chat.completions.create(

                    model="gpt-4.1-mini",

                    messages=[

                        {
                            "role": "system",
                            "content": """
                            คุณคือ AI Logistics Assistant

                            ตอบเฉพาะข้อมูลที่มีใน Excel เท่านั้น
                            ถ้าไม่มีข้อมูลให้ตอบว่า:
                            'ไม่พบข้อมูล'
                            """
                        },

                        {
                            "role": "user",
                            "content": f"""
                            ข้อมูลทั้งหมด:

                            {filtered_data}

                            คำถาม:
                            {text}
                            """
                        }
                    ]
                )

                reply = response.choices[0].message.content

            except Exception as e:

                reply = str(e)
       
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