import os
from flask import Flask, request, render_template, redirect, session
import os

from dotenv import load_dotenv
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
courier_df = pd.read_excel("courier.xlsx")
cross_df = pd.read_excel("cross_border.xlsx")
packing_df = pd.read_excel("packing.xlsx")
customs_df = pd.read_excel("customs_clearance.xlsx")
insurance_df = pd.read_excel("cargo_insurance.xlsx")
reefer_df = pd.read_excel("tracking_reefer.xlsx")
users_df = pd.read_excel("users.xlsx")
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
    password TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS action_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    action TEXT,

    target TEXT,

    action_time TEXT

)
""")

conn.commit()
from datetime import datetime
def log_action(
    username,
    action,
    target
):

    cursor.execute(

        """
        INSERT INTO action_logs
        (
            username,
            action,
            target,
            action_time
        )
        VALUES
        (?, ?, ?, ?)
        """,

        (
            username,
            action,
            target,
            datetime.now(
                ZoneInfo("Asia/Bangkok")
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

    )

    conn.commit()

# SESSION TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (

    user_id TEXT,

    username TEXT,

    display_name TEXT,

    login_time TEXT,

    last_active TEXT
)
""")


conn.commit()

# LOGIN HISTORY TABLE

cursor.execute("""

CREATE TABLE IF NOT EXISTS login_history (

    user_id TEXT,

    username TEXT,

    display_name TEXT,

    login_time TEXT

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
    category TEXT,
    keyword TEXT,
    answer TEXT
)
""")

conn.commit()


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
CREATE TABLE IF NOT EXISTS courier_service (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
   
    company TEXT,
    contact TEXT,
    email TEXT,
    tel TEXT,
    service_type TEXT,
    base_location TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS faq_categories (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    category_name TEXT

)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customs_service (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company TEXT,
    contact TEXT,
    email TEXT,
    tel TEXT,
    base TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS packing_service(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company TEXT,
    contact TEXT,
    email TEXT,
    tel TEXT,
    service TEXT,
    base TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cross_border_service(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company TEXT,
    contact TEXT,
    email TEXT,
    tel TEXT,
    route TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS insurance_service(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company TEXT,
    department TEXT,
    contact TEXT,
    email TEXT,
    tel TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS trucking_service(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company TEXT,
    contact TEXT,
    email TEXT,
    tel TEXT,
    type TEXT,
    base TEXT

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

DEBUG_MODE = True

# =========================
# LINE API
# =========================

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# =========================
# LOGIN SESSION
# =========================

COMPANY_PASSWORD = "BDVM2026"
ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD"
)

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
# ADMIN PANEL
# =========================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    # =========================
    # LOGIN
    # =========================

    if "admin_logged_in" not in session:

        if request.method == "POST":

            username = request.form["username"]

            password = request.form["password"]

            if (
                username == ADMIN_USERNAME
                and
                password == ADMIN_PASSWORD
            ):

                session["admin_logged_in"] = True
                session["admin_username"] = username

                return redirect("/admin")

            return """

            <h3>
            ❌ WRONG USERNAME OR PASSWORD
            </h3>

            <a href="/admin">
            BACK
            </a>

            """

        return """

<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8">

<meta
name="viewport"
content="width=device-width, initial-scale=1.0"
>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{

    font-family:Arial,sans-serif;

    background:
    linear-gradient(
        135deg,
        #0F95F5,
        #5B9BF0
    );

    height:100vh;

    display:flex;
    justify-content:center;
    align-items:center;

    padding:20px;
}

.login-card{

    width:100%;
    max-width:420px;

    background:
    rgba(255,255,255,0.15);

    backdrop-filter:blur(12px);

    border:
    1px solid rgba(255,255,255,0.2);

    border-radius:25px;

    padding:40px 30px;

    text-align:center;

    box-shadow:
    0 8px 30px rgba(0,0,0,0.2);

    animation:fadeIn 0.6s ease;
}

@keyframes fadeIn{

    from{
        opacity:0;
        transform:translateY(20px);
    }

    to{
        opacity:1;
        transform:translateY(0);
    }
}

.logo{

    width:120px;

    margin-bottom:20px;

    border-radius:20px;

    box-shadow:
    0 4px 20px rgba(0,0,0,0.2);
}

h2{

    color:white;

    margin-bottom:10px;

    font-size:30px;
}

.subtitle{

    color:white;

    opacity:0.9;

    margin-bottom:25px;

    font-size:14px;
}

input{

    width:100%;

    padding:14px;

    margin-top:15px;

    border:none;

    border-radius:12px;

    font-size:15px;

    outline:none;
}

button{

    width:100%;

    padding:14px;

    margin-top:20px;

    border:none;

    border-radius:12px;

    background:white;

    color:#0F95F5;

    font-size:16px;

    font-weight:bold;

    cursor:pointer;

    transition:0.3s;
}

button:hover{

    transform:scale(1.03);
}

.footer{

    margin-top:20px;

    color:white;

    font-size:13px;

    opacity:0.8;
}

</style>

</head>

<body>

<div class="login-card">

    <img
        class="logo"
        src="/static/logo.png"
    >

    <h2>
    🔐 ADMIN LOGIN
    </h2>

    <p class="subtitle">
    กรุณาเข้าสู่ระบบเพื่อจัดการผู้ใช้งาน
    </p>

    <form method="POST">

        <input
            name="username"
            placeholder="Username"
            autocomplete="off"
        >

        <input
            type="password"
            name="password"
            placeholder="Password"
            autocomplete="new-password"
        >

        <button type="submit">
            LOGIN
        </button>

    </form>

    <div class="footer">
    BDVM BOT MANAGEMENT SYSTEM
    </div>

</div>

</body>

</html>

"""

    # =========================
    # ADMIN PAGE
    # =========================

    cursor.execute(
        """
        SELECT username,status
        FROM users
        """
    )

    users = cursor.fetchall()

    html = """

    <!DOCTYPE html>

    <html>

    <head>

    <style>

    *{
        margin:0;
        padding:0;
        box-sizing:border-box;
    }

    body{

        font-family:Arial,sans-serif;

        background:
        linear-gradient(
            135deg,
            #0F95F5,
            #5B9BF0
        );

        min-height:100vh;

        padding:40px;
    }

    .container{

        max-width:900px;

        margin:auto;

        background:white;

        padding:30px;

        border-radius:25px;

        box-shadow:
        0 10px 30px rgba(0,0,0,0.2);
    }

    h2{

        color:#0F95F5;

        margin-bottom:20px;

        text-align:center;
    }

    .top-buttons{

        text-align:center;

        margin-bottom:25px;
    }

    .top-buttons a{

        text-decoration:none;

        background:#0F95F5;

        color:white;

        padding:10px 18px;

        border-radius:12px;

        margin:5px;

        display:inline-block;

        transition:0.3s;
    }

    .top-buttons a:hover{

        transform:scale(1.05);
    }

    form{

        margin-bottom:25px;
    }

    input{

        width:100%;

        padding:14px;

        margin-top:12px;

        border:none;

        border-radius:12px;

        background:#f1f1f1;
 
        font-size:15px;
    }

    button{

        width:100%;

        padding:14px;

        margin-top:15px;

        border:none;

        border-radius:12px;

        background:#0F95F5;

        color:white;

        font-size:16px;

        font-weight:bold;

        cursor:pointer;

        transition:0.3s;
    }

    button:hover{

        transform:scale(1.02);
    }

    .user-card{

        background:#f8f9ff;

        padding:18px;

        border-radius:15px;

        margin-top:15px;

        box-shadow:
        0 3px 10px rgba(0,0,0,0.08);
    }

    .user-card a{

        text-decoration:none;

        margin-right:15px;

        font-weight:bold;
    }

    .delete{

        color:red;
    }

    .reset{

        color:orange;
    }

    hr{

        margin:30px 0;
    }

    </style>

    </head>

    <body>

    <div class="container">

    <h2>
    👨‍💼 USER MANAGEMENT
    </h2>

    <div class="top-buttons">

    <a href="/dashboard">
    📈 DASHBOARD
    </a>

    <a href="/action_logs">
    📋 ACTION LOGS
    </a>

    <a href="/admin_logout">
    🚪 LOGOUT
    </a>

    <a href="/login_logs">
    📊 LOGIN LOGS
    </a>

    <a href="/login_history">
    📜 LOGIN HISTORY
    </a>

    <a href="/courier_management">
    🚚 COURIER
    </a>

    <a href="/customs_management">
    📄 CUSTOMS MANAGEMENT
    </a>

    <a href="/packing_management">
    📦 PACKING MANAGEMENT
    </a>

    <a href="/cross_management">
    🌏 CROSS BORDER MANAGEMENT
    </a>

    <a href="/insurance_management">
    🛡 INSURANCE MANAGEMENT
    </a>

    <a href="/trucking_management">
    🚛 TRUCKING MANAGEMENT
    </a>

    <a href="/faq_management">
    📚 FAQ MANAGEMENT
    </a>

    <a href="/faq_category_management">
    📂 FAQ CATEGORY
    </a>

    </div>

    <hr>

    <h3>
    ➕ ADD USER
    </h3>

    <form
        method="POST"
        action="/add_user"
        autocomplete="off"
    >

        <input
            name="username"
            placeholder="Username"
            autocomplete="off"
        >

        <input
            type="password"
            name="password"
            placeholder="Password"
           autocomplete="new-password"
        >

        <button type="submit">
             ADD USER
        </button>

    </form>

    <hr>

    <h3>
    📄 Upload Excel
    </h3>

    <form
        action="/upload_excel"
        method="POST"
        enctype="multipart/form-data"
    >

        <input
            type="file"
            name="file"
        >

        <button type="submit">
            Upload
        </button>

    </form>

    <hr>

    <h3>
    👥 USER LIST
    </h3>

    """

    for user in users:

        status_color = (
            "🟢 ACTIVE"
            if user[1] == "active"
            else "🔴 INACTIVE"
        )

        html += f"""

        <div class="user-card">

            <h3>
            👤 {user[0]}
            </h3>

            <p>
            {status_color}
            </p>

            <br>

            <a
                href="/disable_user/{user[0]}"
            >
                🔴 DISABLE
            </a>

            <a
                href="/enable_user/{user[0]}"
            >
                🟢 ENABLE
            </a>

            <br><br>

            <a
                class="delete"
                href="/delete_user/{user[0]}"
            >
                🗑 DELETE
            </a>

            <a
                class="reset"
                href="/reset_password/{user[0]}"
            >
                🔑 RESET PASSWORD
            </a>

        </div>

        """

    html += """

    </div>

    </body>

    </html>

    """
    return html

# =========================
# UPLOAD EXCEL
# =========================

@app.route(
    "/upload_excel",
    methods=["POST"]
)
def upload_excel():

    global courier_df
    global customs_df
    global packing_df
    global cross_df
    global insurance_df
    global reefer_df
    global users_df

    file = request.files["file"]

    filename = file.filename

    file.save(filename)

    # =========================
    # USERS
    # =========================

    if filename == "users.xlsx":

        users_df = pd.read_excel(
            "users.xlsx"
        )

        for index, row in users_df.iterrows():

            username = str(
                row["username"]
            ).strip()

            password = str(
                row["password"]
            ).strip()

            hashed_password = generate_password_hash(
                password
            )

            cursor.execute(
                "SELECT * FROM users WHERE username=?",
                (username,)
            )

            existing = cursor.fetchone()

            # UPDATE
            if existing:

                cursor.execute(

                    """
                    UPDATE users
                    SET password=?
                    WHERE username=?
                    """,

                    (
                        hashed_password,
                        username
                    )
                )

            # INSERT
            else:

                cursor.execute(

                    """
                    INSERT INTO users
                    VALUES (?, ?, ?)
                    """,

                    (
                        username,
                        hashed_password,
                        "active"
                    )
                )

        conn.commit()
        os.remove(filename)

    # =========================
    # COURIER
    # =========================

    elif filename == "courier.xlsx":

        courier_df = pd.read_excel(
            "courier.xlsx"
        )

        cursor.execute(
            "DELETE FROM courier_service"
        )

        for index, row in courier_df.iterrows():

            cursor.execute(

                """
                INSERT INTO courier_service
                (
                    company,
                    contact,
                    email,
                    tel,
                    service_type,
                    base_location
                )
                VALUES
                (?, ?, ?, ?, ?, ?)
                """,

                (
                    str(row["company"]),
                    str(row["contact"]),
                    str(row["email"]),
                    str(row["tel"]),
                    "",
                    ""
                )

            )

        conn.commit()
        os.remove(filename)


    # =========================
    # CUSTOMS
    # =========================
 
    elif filename == "customs_clearance.xlsx":

        customs_df = pd.read_excel(
            "customs_clearance.xlsx"
        )

        cursor.execute(
            "DELETE FROM customs_service"
        )

        for index, row in customs_df.iterrows():

            cursor.execute(

                """
                INSERT INTO customs_service
                (
                    company,
                    contact,
                    email,
                    tel,
                    base
                )
                VALUES
                (?, ?, ?, ?, ?)
                """,

                (
                    str(row["company"]),
                    str(row["contact"]),
                    str(row["email"]),
                    str(row["tel"]),
                    str(row["base"])
                )

            )

        conn.commit()
        os.remove(filename)

    # =========================
    # PACKING
    # =========================

    elif filename == "packing.xlsx":

        packing_df = pd.read_excel(
            "packing.xlsx"
        )

        cursor.execute(
            "DELETE FROM packing_service"
        )

        for index,row in packing_df.iterrows():

            cursor.execute(

                """
                INSERT INTO packing_service
                (
                    company,
                    contact,
                    email,
                    tel,
                    service,
                    base
                )
                VALUES
                (?, ?, ?, ?, ?, ?)
                """,

                (
                    str(row["company"]),
                    str(row["contact"]),
                    str(row["email"]),
                    str(row["tel"]),
                    str(row["service"]),
                    str(row["base"])
                )

            )

        conn.commit()
    # =========================
    # CROSS BORDER
    # =========================

    elif filename == "cross_border.xlsx":

        cross_df = pd.read_excel(
            "cross_border.xlsx"
        )

        cursor.execute(
            "DELETE FROM cross_border_service"
        )

        for index,row in cross_df.iterrows():

            cursor.execute(

                """
                INSERT INTO cross_border_service
                (
                    company,
                    contact,
                    email,
                    tel,
                    route
                )
                VALUES
                (?, ?, ?, ?, ?)
                """,

                (
                    str(row["company"]),
                    str(row["contact"]),
                    str(row["email"]),
                    str(row["tel"]),
                    str(row["route"])
                )

            )

        conn.commit()

    # =========================
    # INSURANCE
    # =========================

    elif filename == "cargo_insurance.xlsx":

        insurance_df = pd.read_excel(
            "cargo_insurance.xlsx"
        )

        cursor.execute(
            "DELETE FROM insurance_service"
        )

        for index,row in insurance_df.iterrows():

            cursor.execute(

                """
                INSERT INTO insurance_service
                (
                    company,
                    department,
                    contact,
                    email,
                    tel
                )
                VALUES
                (?, ?, ?, ?, ?)
                """,

                (
                    str(row["company"]),
                    str(row["department"]),
                    str(row["contact"]),
                    str(row["email"]),
                    str(row["tel"])
                )

            )

        conn.commit()

    # =========================
    # TRUCKING
    # =========================

    elif filename == "tracking_reefer.xlsx":

        reefer_df = pd.read_excel(
            "tracking_reefer.xlsx"
        )

        cursor.execute(
            "DELETE FROM trucking_service"
        )

        for index,row in reefer_df.iterrows():

            cursor.execute(

                """
                INSERT INTO trucking_service
                (
                    company,
                    contact,
                    email,
                    tel,
                    type,
                    base
                )
                VALUES
                (?, ?, ?, ?, ?, ?)
                """,

                (
                    str(row["company"]),
                    str(row["contact"]),
                    str(row["email"]),
                    str(row["tel"]),
                    str(row["Type"]),
                    str(row["Base"])
                )

            )

        conn.commit()

    log_action(
        "admin",
        "UPLOAD FILE",
        filename
    )
    return f"""

    <h2>
    ✅ Upload Success
    </h2>

    <p>
    FILE:
    {filename}
    </p>

    <a href="/admin">
    🔙 BACK
    </a>

    """

# =========================
# ADMIN LOGOUT
# =========================

@app.route("/admin_logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect("/admin")

# =========================
# ADD USER
# =========================

@app.route("/add_user", methods=["POST"])
def add_user():

    username = request.form["username"]

    password = request.form["password"]

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    existing = cursor.fetchone()

    if existing:

        return "USERNAME ALREADY EXISTS"

    hashed_password = generate_password_hash(
        password
    )

    cursor.execute(

        """
        INSERT INTO users
        VALUES (?, ?, ?)
        """,

        (
            username,
            hashed_password,
            "active"
        )
    )

    conn.commit()

    log_action(
        "admin",
        "ADD USER",
        username
    )

    return redirect("/admin")

# =========================
# DELETE USER
# =========================

@app.route("/disable_user/<username>")
def disable_user(username):

    print(
        "DISABLE USER:",
        username
    )

    cursor.execute(
        """
        UPDATE users
        SET status='inactive'
        WHERE username=?
        """,
        (username,)
    )

    conn.commit()

    log_action(
        "admin",
        "DISABLE USER",
        username
    )

    return redirect("/admin")

@app.route("/enable_user/<username>")
def enable_user(username):

    cursor.execute(
        """
        UPDATE users
        SET status='active'
        WHERE username=?
        """,
        (username,)
    )

    conn.commit()

    log_action(
        "admin",
        "ENABLE USER",
        username
    )

    return redirect("/admin")

@app.route("/delete_user/<username>")
def delete_user(username):

    cursor.execute(
        """
        DELETE FROM users
        WHERE username=?
        """,
        (username,)
    )

    conn.commit()

    log_action(
        "admin",
        "DELETE USER",
        username
    )

    return redirect("/admin")

# =========================
# RESET PASSWORD
# =========================

@app.route("/reset_password/<username>")
def reset_password(username):

    new_password = "1234"

    hashed_password = generate_password_hash(
        new_password
    )

    cursor.execute(
        """
        UPDATE users
        SET password=?
        WHERE username=?
        """,
        (
            hashed_password,
            username
        )
    )

    conn.commit()

    log_action(
        "admin",
        "RESET PASSWORD",
        username
    )

    return f"""
    ...
    """
# =========================
# ACTION LOGS
# =========================
@app.route("/action_logs")
def action_logs():

    cursor.execute(
        """
        SELECT
        username,
        action,
        target,
        action_time

        FROM action_logs

        ORDER BY id DESC
        """
    )

    logs = cursor.fetchall()

    html = """

    <html>

    <body>

    <h1>
    📋 ACTION LOGS
    </h1>

    """

    for log in logs:

        html += f"""

        <div
        style="
        border:1px solid #ddd;
        padding:10px;
        margin:10px;
        border-radius:10px;
        ">

        👤 {log[0]}

        <br>

        ⚙ {log[1]}

        <br>

        🎯 {log[2]}

        <br>

        🕒 {log[3]}

        </div>

        """

    html += """

    <br>

    <a href="/admin">

    🔙 Back

    </a>

    </body>

    </html>

    """

    return html

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

<meta
name="viewport"
content="width=device-width, initial-scale=1.0"
>

<script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{

    font-family:Arial,sans-serif;

    background:
    linear-gradient(
        135deg,
        #0F95F5,
        #5B9BF0
    );

    height:100vh;

    display:flex;
    justify-content:center;
    align-items:center;

    padding:20px;
}

.card{

    animation:fadeIn 0.6s ease;
}

@keyframes fadeIn{

    from{
        opacity:0;
        transform:translateY(20px);
    }

    to{
        opacity:1;
        transform:translateY(0);
    }
}

.logo{

    width:180px;

    display:block;

    margin:0 auto 20px auto;

    border-radius:20px;

    box-shadow:
    0 4px 20px rgba(0,0,0,0.2);
}

h1{

    font-size:28px;
    margin-bottom:8px;
}

.subtitle{

    font-size:14px;
    opacity:0.9;
    margin-bottom:25px;
}

input{

    width:100%;

    padding:14px;

    margin-top:15px;

    border:none;

    border-radius:12px;

    font-size:15px;

    outline:none;
}

button{

    width:100%;

    padding:14px;

    margin-top:20px;

    border:none;

    border-radius:12px;

    background:white;

    color:#072BF2;

    font-weight:bold;

    font-size:16px;

    cursor:pointer;

    transition:0.3s;
}

button:hover{

    transform:scale(1.03);
}

button:disabled{

    opacity:0.7;
}

#msg{

    margin-top:18px;

    font-size:14px;

    font-weight:bold;
}

.loading{

    animation:blink 1s infinite;
}

@keyframes blink{

    0%{opacity:1;}
    50%{opacity:0.5;}
    100%{opacity:1;}
}

</style>

</head>

<body>

<div class="card">

    <img
        class="logo"
        src="/static/logo.png"
    >

    <h1>BDVM BOT</h1>

    <p class="subtitle">
        กรุณาเข้าสู่ระบบเพื่อใช้งาน
    </p>

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
        id="loginBtn"
        onclick="login()"
    >
        Login
    </button>

    <p id="msg"></p>

</div>

<script>

async function initializeLiff(){

    await liff.init({
        liffId:"2010152202-xzzmHkWl"
    });

    if(!liff.isLoggedIn()){

        liff.login();

        return;
    }
}

initializeLiff();

async function login(){

    try{

        const btn =
        document.getElementById("loginBtn");

        btn.disabled = true;

        const msg =
        document.getElementById("msg");

        msg.innerHTML =
        "<span class='loading'>⏳ กำลังเข้าสู่ระบบ...</span>";

        const username =
        document.getElementById("username").value;

        const password =
        document.getElementById("password").value;

        const response =
        await fetch("/check_login",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                username:username,
                password:password
            })

        });

        const result =
        await response.text();

        if(result !== "SUCCESS"){

            msg.innerHTML =
            "❌ Username หรือ Password ไม่ถูกต้อง";

            btn.disabled = false;

            return;
        }

        const urlParams =
        new URLSearchParams(window.location.search);

        const lineUserId =
        urlParams.get("user_id");

        const profile =
        await liff.getProfile();

        const displayName =
        profile.displayName;

        await fetch("/save_user",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                user_id:lineUserId,

                username:username,

                display_name:displayName

            })

        });

        msg.innerHTML =
        "✅ LOGIN SUCCESS";

        setTimeout(()=>{

            liff.closeWindow();

        },1000);

    }

    catch(err){

        alert(err);

        document
        .getElementById("loginBtn")
        .disabled = false;
    }
}

document
.getElementById("password")
.addEventListener("keypress",function(e){

    if(e.key === "Enter"){

        login();
    }
});

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

    display_name = data.get(
        "display_name"
    )
    username = data.get(
        "username"
    )

    current_time = datetime.now(

        ZoneInfo("Asia/Bangkok")

    ).strftime(

        "%d/%m/%Y %H:%M:%S"
    )

    # SAVE LOGIN HISTORY

    cursor.execute(

        """
        INSERT INTO login_history
        VALUES (?, ?, ?, ?)
        """,

        (
            user_id,
            username,
            display_name,
            current_time
        )
    )

    conn.commit()
    cursor.execute(
        "SELECT * FROM sessions WHERE user_id=?",
        (user_id,)
    )

    existing = cursor.fetchone()

    # NEW USER
    if not existing:

        cursor.execute(

            """
            INSERT INTO sessions
            VALUES (?, ?, ?, ?, ?)
            """,

            (
                user_id,
                username,
                display_name,
                current_time,
                current_time
            )
        )

    # UPDATE LAST ACTIVE
    else:

        cursor.execute(

            """
            UPDATE sessions
            SET last_active=?
            WHERE user_id=?
            """,

            (
                current_time,
                user_id
            )
        )

    conn.commit()

    if DEBUG_MODE:

        print(

            "SAVE USER:",

            display_name,
 
            user_id

        )

    return "OK"

# =========================
# IMPORT USERS FROM EXCEL
# =========================

for index, row in users_df.iterrows():

    username = str(row["username"]).strip()

    password = str(row["password"]).strip()

    hashed_password = generate_password_hash(
        password
    )

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    existing = cursor.fetchone()

    # =========================
    # UPDATE PASSWORD
    # =========================

    if existing:

        cursor.execute(

            """
            UPDATE users
            SET password=?
            WHERE username=?
            """,

            (
                hashed_password,
                username
            )
        )

    # =========================
    # INSERT NEW USER
    # =========================

    else:

        cursor.execute(

            """
            INSERT INTO users
            VALUES (?, ?, ?)
            """,

            (
                username,
                hashed_password,
                "active"
            )
        )

conn.commit()

# =========================
# LOGIN LOGS
# =========================

@app.route("/login_logs")
def login_logs():

    if "admin_logged_in" not in session:

        return redirect("/admin")

    cursor.execute(
        "SELECT * FROM sessions"
    )

    records = cursor.fetchall()

    html = """

<!DOCTYPE html>

<html>

<head>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{

    font-family:Arial,sans-serif;

    background:
    linear-gradient(
        135deg,
        #FC3F00,
        #FCFC00
    );

    min-height:100vh;

    padding:40px;
}

.container{

    max-width:1100px;

    margin:auto;

    background:white;

    padding:30px;

    border-radius:25px;

    box-shadow:
    0 10px 30px rgba(0,0,0,0.2);
}

h2{

    text-align:center;

    color:#0F95F5;

    margin-bottom:25px;
}

.top-buttons{

    text-align:center;

    margin-bottom:25px;
}

.top-buttons a{

    text-decoration:none;

    background:#0F95F5;

    color:white;

    padding:10px 18px;

    border-radius:12px;

    margin:5px;

    display:inline-block;
}

.user-card{

    background:#FCFC00;

    padding:18px;

    border-radius:18px;

    margin-top:18px;

    box-shadow:
    0 3px 10px rgba(0,0,0,0.08);
}

.info{

    margin-top:8px;

    color:#444;
}

</style>

</head>

<body>

<div class="container">

<h2>
📊 LOGIN LOGS
</h2>

<div class="top-buttons">

<a href="/admin">
🏠 ADMIN
</a>

<a href="/login_history">
📜 LOGIN HISTORY
</a>

</div>

"""

    for row in records:

        html += f"""

<div class="user-card">

    <h3>
    👤 {row[1]}
    </h3>

    <div class="info">
    LINE NAME:
    {row[2]}
    </div>

    <div class="info">
    LOGIN TIME:
    {row[3]}
    </div>

    <div class="info">
    LAST ACTIVE:
    {row[4]}
    </div>

</div>

"""

    html += """

</div>

</body>

</html>

"""

    return html

# =========================
# LOGIN HISTORY
# =========================

@app.route("/login_history")
def login_history():

    if "admin_logged_in" not in session:

        return redirect("/admin")

    cursor.execute(

        """
        SELECT * FROM login_history
        ORDER BY rowid DESC
        """
    )

    records = cursor.fetchall()

    html = """

<!DOCTYPE html>

<html>

<head>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{

    font-family:Arial,sans-serif;

    background:
    linear-gradient(
        135deg,
        #7D33B4,
        #00FFEA
    );

    min-height:100vh;

    padding:40px;
}

.container{

    max-width:1100px;

    margin:auto;

    background:white;

    padding:30px;

    border-radius:25px;

    box-shadow:
    0 10px 30px rgba(0,0,0,0.2);
}

h2{

    text-align:center;

    color:#0F95F5;

    margin-bottom:25px;
}

.top-buttons{

    text-align:center;

    margin-bottom:25px;
}

.top-buttons a{

    text-decoration:none;

    background:#0F95F5;

    color:white;

    padding:10px 18px;

    border-radius:12px;

    margin:5px;

    display:inline-block;
}

.history-card{

    background:#0FBDFF;

    padding:18px;

    border-radius:18px;

    margin-top:18px;

    box-shadow:
    0 3px 10px rgba(0,0,0,0.08);
}

.info{

    margin-top:8px;

    color:#FC0388;
}

</style>

</head>

<body>

<div class="container">

<h2>
📜 LOGIN HISTORY
</h2>

<div class="top-buttons">

<a href="/admin">
🏠 ADMIN
</a>

<a href="/login_logs">
📊 LOGIN LOGS
</a>

</div>

"""

    for row in records:

        html += f"""

<div class="history-card">

    <h3>
    👤 {row[1]}
    </h3>

    <div class="info">
    LINE NAME:
    {row[2]}
    </div>

    <div class="info">
    LOGIN TIME:
    {row[3]}
    </div>

</div>

"""

    html += """

</div>

</body>

</html>

"""

    return html

@app.route("/check_action_logs")
def check_action_logs():

    cursor.execute(
        "SELECT * FROM action_logs"
    )

    return str(cursor.fetchall())

@app.route("/test_log")
def test_log():

    log_action(
        "admin",
        "TEST",
        "system"
    )

    return "OK"

@app.route("/courier_management")
def courier_management():

    cursor.execute(
        """
        SELECT *
        FROM courier_service
        """
    )

    records = cursor.fetchall()

    html = """

    <h1>
    🚚 COURIER MANAGEMENT
    </h1>

    <form
        method="POST"
        action="/add_courier"
    >

    Company

    <input name="company">

    Contact

    <input name="contact">

    Email

    <input name="email">

    Tel

    <input name="tel">

    <button>
    SAVE
    </button>

    </form>

    <hr>

    """

    for row in records:

        html += f"""

        <div
        style="
        border:1px solid #ddd;
        padding:15px;
        margin-bottom:10px;
        border-radius:10px;
        "
        >

        <b>Company:</b> {row[1]}

        <br>

        <b>Contact:</b> {row[2]}

        <br>

        <b>Email:</b> {row[3]}

        <br>
 
        <b>Tel:</b> {row[4]}

        <br><br>

        <a href="/edit_courier/{row[0]}">
        ✏️ EDIT
        </a>

        <a href="/delete_courier/{row[0]}">
        🗑 DELETE
        </a>

        </div>

        """

    html += """
    <br>
    <a href="/admin">
    🔙 BACK
    </a>
    """

    return html

@app.route(
    "/add_courier",
    methods=["POST"]
)
def add_courier():

    cursor.execute(

    """
    INSERT INTO courier_service
    (
        company,
        contact,
        email,
        tel,
        service_type,
        base_location
    )
    VALUES
    (?, ?, ?, ?, ?, ?)
    """,

    (
        request.form["company"],
        request.form["contact"],
        request.form["email"],
        request.form["tel"],
        "",
        ""
    )

)

    conn.commit()

    log_action(
        "admin",
        "ADD COURIER",
        request.form["company"]
    )

    return redirect(
        "/courier_management"
    )

@app.route("/delete_courier/<int:id>")
def delete_courier(id):

    cursor.execute(
        """
        DELETE FROM courier_service
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()

    return redirect(
        "/courier_management"
    )

@app.route("/edit_courier/<int:id>")
def edit_courier(id):

    cursor.execute(
        """
        SELECT *
        FROM courier_service
        WHERE id=?
        """,
        (id,)
    )

    row = cursor.fetchone()

    return f"""

    <h1>
    ✏️ EDIT COURIER
    </h1>

    <form
        method="POST"
        action="/update_courier/{id}"
    >

    Company

    <input
        name="company"
        value="{row[1]}"
    >

    <br><br>

    Contact

    <input
        name="contact"
        value="{row[2]}"
    >

    <br><br>

    Email

    <input
        name="email"
        value="{row[3]}"
    >

    <br><br>

    Tel

    <input
        name="tel"
        value="{row[4]}"
    >

    <br><br>

    <button>
    UPDATE
    </button>

    </form>

    """

@app.route(
    "/update_courier/<int:id>",
    methods=["POST"]
)
def update_courier(id):

    company = request.form["company"]
    contact = request.form["contact"]
    email = request.form["email"]
    tel = request.form["tel"]

    cursor.execute(

        """
        UPDATE courier_service
        SET
            company=?,
            contact=?,
            email=?,
            tel=?
        WHERE id=?
        """,

        (
            company,
            contact,
            email,
            tel,
            id
        )

    )

    conn.commit()

    return redirect(
        "/courier_management"
    )

@app.route("/check_courier_table")
def check_courier_table():

    cursor.execute(
        "PRAGMA table_info(courier_service)"
    )

    return str(cursor.fetchall())

@app.route("/customs_management")
def customs_management():

    cursor.execute(
        """
        SELECT *
        FROM customs_service
        """
    )

    records = cursor.fetchall()

    html = """

    <h1>
    📄 CUSTOMS MANAGEMENT
    </h1>

    """

    html += """

    <form
    method="POST"
    action="/add_customs"
    >

    Company

    <input name="company">

    Contact

    <input name="contact">

    Email

    <input name="email">

    Tel

    <input name="tel">

    Base

    <input name="base">

    <button>
    SAVE
    </button>

    </form>

    <hr>

    """

    for row in records:

        html += f"""

        <div
        style="
        border:1px solid #ddd;
        padding:15px;
        margin-bottom:10px;
        border-radius:10px;
        "
        >

        <b>Company:</b> {row[1]}
        <br>

        <b>Contact:</b> {row[2]}
        <br>

        <b>Email:</b> {row[3]}
        <br>

        <b>Tel:</b> {row[4]}
        <br>

        <b>Base:</b> {row[5]}
        <br><br>

        <a href="/delete_customs/{row[0]}">
        🗑 DELETE
        </a>

        </div>

        """

    html += """

    <br>

    <a href="/admin">
    🔙 BACK
    </a>

    """

    return html

@app.route("/delete_customs/<int:id>")
def delete_customs(id):

    cursor.execute(
        """
        DELETE FROM customs_service
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()

    return redirect(
        "/customs_management"
    )

@app.route(
    "/add_customs",
    methods=["POST"]
)
def add_customs():

    cursor.execute(

        """
        INSERT INTO customs_service
        (
            company,
            contact,
            email,
            tel,
            base
        )
        VALUES
        (?, ?, ?, ?, ?)
        """,

        (
            request.form["company"],
            request.form["contact"],
            request.form["email"],
            request.form["tel"],
            request.form["base"]
        )

    )

    conn.commit()

    return redirect(
        "/customs_management"
    )

@app.route("/edit_customs/<int:id>")
def edit_customs(id):

    cursor.execute(
        """
        SELECT *
        FROM customs_service
        WHERE id=?
        """,
        (id,)
    )

    row = cursor.fetchone()

    return f"""

    <h1>
    ✏️ EDIT C
    </h1>

    <form
        method="POST"
        action="/update_customs/{id}"
    >

    Company

    <input
        name="company"
        value="{row[1]}"
    >

    <br><br>

    Contact

    <input
        name="contact"
        value="{row[2]}"
    >

    <br><br>

    Email

    <input
        name="email"
        value="{row[3]}"
    >

    <br><br>

    Tel

    <input
        name="tel"
        value="{row[4]}"
    >

    <br><br>

    Base

    <input
        name="base"
        value="{row[5]}"
    >
    <br><br>

    <button>
    UPDATE
    </button>

    </form>

    """
@app.route("/check_customs")
def check_customs():

    cursor.execute(
        "SELECT * FROM customs_service"
    )

    return str(
        cursor.fetchall()
    )

@app.route("/packing_management")
def packing_management():

    cursor.execute(
        """
        SELECT *
        FROM packing_service
        """
    )

    records = cursor.fetchall()

    html = """

    <h1>
    📦 PACKING MANAGEMENT
    </h1>

    <form
    method="POST"
    action="/add_packing"
    >

    Company
    <input name="company">

    Contact
    <input name="contact">

    Email
    <input name="email">

    Tel
    <input name="tel">

    Service
    <input name="service">

    Base
    <input name="base">

    <button>
    SAVE
    </button>

    </form>

    <hr>

    """

    for row in records:

        html += f"""

        <div
        style="
        border:1px solid #ddd;
        padding:15px;
        margin-bottom:10px;
        border-radius:10px;
        "
        >

        <b>Company:</b> {row[1]}
        <br>

        <b>Contact:</b> {row[2]}
        <br>

        <b>Email:</b> {row[3]}
        <br>

        <b>Tel:</b> {row[4]}
        <br>

        <b>Service:</b> {row[5]}
        <br>

        <b>Base:</b> {row[6]}
        <br><br>

        <a href="/edit_packing/{row[0]}">
        ✏️ EDIT
        </a>

        &nbsp;&nbsp;

        <a href="/delete_packing/{row[0]}">
        🗑 DELETE
        </a>

        </div>

        """

    html += """

    <br>

    <a href="/admin">
    🔙 BACK
    </a>

    """

    return html

@app.route("/delete_packing/<int:id>")
def delete_packing(id):

    cursor.execute(
        """
        DELETE FROM packing_service
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()

    return redirect(
        "/packing_management"
    )

@app.route(
    "/add_packing",
    methods=["POST"]
)
def add_packing():

    cursor.execute(

        """
        INSERT INTO packing_service
        (
            company,
            contact,
            email,
            tel,
            service,
            base
        )
        VALUES
        (?, ?, ?, ?, ?, ?)
        """,

        (
            request.form["company"],
            request.form["contact"],
            request.form["email"],
            request.form["tel"],
            request.form["service"],
            request.form["base"]
        )

    )

    conn.commit()

    return redirect(
        "/packing_management"
    )

@app.route("/edit_packing/<int:id>")
def edit_packing(id):

    cursor.execute(
        """
        SELECT *
        FROM packing_service
        WHERE id=?
        """,
        (id,)
    )

    row = cursor.fetchone()

    return f"""

    <h1>
    ✏️ EDIT C
    </h1>

    <form
        method="POST"
        action="/update_packing/{id}"
    >

    Company

    <input
        name="company"
        value="{row[1]}"
    >

    <br><br>

    Contact

    <input
        name="contact"
        value="{row[2]}"
    >

    <br><br>

    Email

    <input
        name="email"
        value="{row[3]}"
    >

    <br><br>

    Tel

    <input
        name="tel"
        value="{row[4]}"
    >

    <br><br>

    Service

    <input
        name="service"
        value="{row[5]}"
    >

    <br><br>

    Base

    <input
        name="base"
        value="{row[6]}"
    >
    <br><br>

    <button>
    UPDATE
    </button>

    </form>

    """
@app.route("/check_packing")
def check_packing():

    cursor.execute(
        "SELECT * FROM packing_service"
    )

    return str(
        cursor.fetchall()
    )

@app.route("/cross_management")
def cross_management():

    cursor.execute(
        """
        SELECT *
        FROM cross_border_service
        """
    )

    records = cursor.fetchall()

    html = """

    <h1>
    🌏 CROSS BORDER MANAGEMENT
    </h1>

    <form
    method="POST"
    action="/add_cross"
    >

    Company
    <input name="company">

    Contact
    <input name="contact">

    Email
    <input name="email">

    Tel
    <input name="tel">

    Route
    <input name="route">

    <button>
    SAVE
    </button>

    </form>

    <hr>

    """

    for row in records:

        html += f"""

        <div
        style="
        border:1px solid #ddd;
        padding:15px;
        margin-bottom:10px;
        border-radius:10px;
        "
        >

        <b>Company:</b> {row[1]}
        <br>

        <b>Contact:</b> {row[2]}
        <br>

        <b>Email:</b> {row[3]}
        <br>

        <b>Tel:</b> {row[4]}
        <br>

        <b>Route:</b> {row[5]}
        <br><br>

        <a href="/edit_cross/{row[0]}">
        ✏️ EDIT
        </a>

        &nbsp;&nbsp;

        <a href="/delete_cross/{row[0]}">
        🗑 DELETE
        </a>

        </div>

        """

    html += """

    <br>

    <a href="/admin">
    🔙 BACK
    </a>

    """

    return html

@app.route(
    "/add_cross",
    methods=["POST"]
)
def add_cross():

    cursor.execute(

        """
        INSERT INTO cross_border_service
        (
            company,
            contact,
            email,
            tel,
            route
        )
        VALUES
        (?, ?, ?, ?, ?)
        """,

        (
            request.form["company"],
            request.form["contact"],
            request.form["email"],
            request.form["tel"],
            request.form["route"]
        )

    )

    conn.commit()

    return redirect(
        "/cross_management"
    )

@app.route("/delete_cross/<int:id>")
def delete_cross(id):

    cursor.execute(
        """
        DELETE FROM cross_border_service
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()

    return redirect(
        "/cross_management"
    )

@app.route("/edit_cross/<int:id>")
def edit_cross(id):

    cursor.execute(
        """
        SELECT *
        FROM cross_border_service
        WHERE id=?
        """,
        (id,)
    )

    row = cursor.fetchone()

    return f"""

    <h1>
    ✏️ EDIT C
    </h1>

    <form
        method="POST"
        action="/update_cross/{id}"
    >

    Company

    <input
        name="company"
        value="{row[1]}"
    >

    <br><br>

    Contact

    <input
        name="contact"
        value="{row[2]}"
    >

    <br><br>

    Email

    <input
        name="email"
        value="{row[3]}"
    >

    <br><br>

    Tel

    <input
        name="tel"
        value="{row[4]}"
    >

    <br><br>

    Route

    <input
        name="route"
        value="{row[5]}"
    >

    <br><br>

    <button>
    UPDATE
    </button>

    </form>

    """

@app.route("/insurance_management")
def insurance_management():

    cursor.execute(
        """
        SELECT *
        """
    )

    records = cursor.fetchall()

    html = """

    <h1>
    🛡 INSURANCE MANAGEMENT
    </h1>

    <form
    method="POST"
    action="/add_insurance"
    >

    Company
    <input name="company">

    Department
    <input name="department">

    Contact
    <input name="contact">

    Email
    <input name="email">

    Tel
    <input name="tel">

    <button>
    SAVE
    </button>

    </form>

    <hr>

    """

    for row in records:

        html += f"""

        <div
        style="
        border:1px solid #ddd;
        padding:15px;
        margin-bottom:10px;
        border-radius:10px;
        "
        >

        <b>Company:</b> {row[1]}
        <br>

        <b>Department:</b> {row[2]}
        <br>

        <b>Contact:</b> {row[3]}
        <br>

        <b>Email:</b> {row[4]}
        <br>

        <b>Tel:</b> {row[5]}
        <br><br>

        <a href="/edit_insurance/{row[0]}">
        ✏️ EDIT
        </a>

        &nbsp;&nbsp;

        <a href="/delete_insurance/{row[0]}">
        🗑 DELETE
        </a>

        </div>

        """

    html += """

    <br>

    <a href="/admin">
    🔙 BACK
    </a>

    """

    return html

@app.route(
    "/add_insurance",
    methods=["POST"]
)
def add_insurance():

    cursor.execute(

        """
        INSERT INTO insurance_service
        (
            company,
            department,
            contact,
            email,
            tel
        )
        VALUES
        (?, ?, ?, ?, ?)
        """,

        (
            request.form["company"],
            request.form["department"],
            request.form["contact"],
            request.form["email"],
            request.form["tel"]
        )

    )

    conn.commit()

    return redirect(
        "/insurance_management"
    )

@app.route("/delete_insurance/<int:id>")
def delete_insurance(id):

    cursor.execute(
        """
        DELETE FROM insurance_service
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()

    return redirect(
        "/insurance_management"
    )

@app.route("/edit_insurance/<int:id>")
def edit_insurance(id):

    cursor.execute(
        """
        SELECT *
        FROM insurance_service
        WHERE id=?
        """,
        (id,)
    )

    row = cursor.fetchone()

    return f"""

    <h1>
    ✏️ EDIT INSURANCE
    </h1>

    <form
    method="POST"
    action="/update_insurance/{id}"
    >

    Company
    <input
    name="company"
    value="{row[1]}"
    >

    <br><br>

    Department
    <input
    name="department"
    value="{row[2]}"
    >

    <br><br>

    Contact
    <input
    name="contact"
    value="{row[3]}"
    >

    <br><br>

    Email
    <input
    name="email"
    value="{row[4]}"
    >

    <br><br>

    Tel
    <input
    name="tel"
    value="{row[5]}"
    >

    <br><br>

    <button>
    UPDATE
    </button>

    </form>

    """

@app.route(
    "/update_insurance/<int:id>",
    methods=["POST"]
)
def update_insurance(id):

    cursor.execute(

        """
        UPDATE insurance_service
        SET
            company=?,
            department=?,
            contact=?,
            email=?,
            tel=?
        WHERE id=?
        """,

        (
            request.form["company"],
            request.form["department"],
            request.form["contact"],
            request.form["email"],
            request.form["tel"],
            id
        )

    )

    conn.commit()

    return redirect(
        "/insurance_management"
    )

@app.route("/check_insurance")
def check_insurance():

    cursor.execute(
        "SELECT * FROM insurance_service"
    )

    return str(
        cursor.fetchall()
    )

@app.route("/trucking_management")
def trucking_management():

    cursor.execute(
        """
        SELECT *
        FROM trucking_service
        """
    )

    records = cursor.fetchall()

    html = """

    <h1>
    🚛 TRUCKING MANAGEMENT
    </h1>

    <form
    method="POST"
    action="/add_trucking"
    >

    Company
    <input name="company">

    Contact
    <input name="contact">

    Email
    <input name="email">

    Tel
    <input name="tel">

    Type
    <input name="type">

    Base
    <input name="base">

    <button>
    SAVE
    </button>

    </form>

    <hr>

    """

    for row in records:

        html += f"""

        <div
        style="
        border:1px solid #ddd;
        padding:15px;
        margin-bottom:10px;
        border-radius:10px;
        "
        >

        <b>Company:</b> {row[1]}
        <br>

        <b>Contact:</b> {row[2]}
        <br>

        <b>Email:</b> {row[3]}
        <br>

        <b>Tel:</b> {row[4]}
        <br>

        <b>Type:</b> {row[5]}
        <br>

        <b>Base:</b> {row[6]}
        <br><br>

        <a href="/edit_trucking/{row[0]}">
        ✏️ EDIT
        </a>

        &nbsp;&nbsp;

        <a href="/delete_trucking/{row[0]}">
        🗑 DELETE
        </a>

        </div>

        """

    html += """

    <br>

    <a href="/admin">
    🔙 BACK
    </a>

    """

    return html

@app.route(
    "/add_trucking",
    methods=["POST"]
)
def add_trucking():

    cursor.execute(

        """
        INSERT INTO trucking_service
        (
            company,
            contact,
            email,
            tel,
            type,
            base
        )
        VALUES
        (?, ?, ?, ?, ?, ?)
        """,

        (
            request.form["company"],
            request.form["contact"],
            request.form["email"],
            request.form["tel"],
            request.form["type"],
            request.form["base"]
        )

    )

    conn.commit()

    return redirect(
        "/trucking_management"
    )

@app.route("/delete_trucking/<int:id>")
def delete_trucking(id):

    cursor.execute(
        """
        DELETE FROM trucking_service
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()

    return redirect(
        "/trucking_management"
    )

@app.route("/edit_trucking/<int:id>")
def edit_trucking(id):

    cursor.execute(
        """
        SELECT *
        FROM trucking_service
        WHERE id=?
        """,
        (id,)
    )

    row = cursor.fetchone()

    return f"""

    <h1>
    ✏️ EDIT TRUCKING
    </h1>

    <form
    method="POST"
    action="/update_trucking/{id}"
    >

    Company
    <input
    name="company"
    value="{row[1]}"
    >

    <br><br>

    Contact
    <input
    name="contact"
    value="{row[2]}"
    >

    <br><br>

    Email
    <input
    name="email"
    value="{row[3]}"
    >

    <br><br>

    Tel
    <input
    name="tel"
    value="{row[4]}"
    >

    <br><br>

    Type
    <input
    name="type"
    value="{row[5]}"
    >

    <br><br>

    Base
    <input
    name="base"
    value="{row[6]}"
    >

    <br><br>

    <button>
    UPDATE
    </button>

    </form>

    """

@app.route(
    "/update_trucking/<int:id>",
    methods=["POST"]
)
def update_trucking(id):

    cursor.execute(

        """
        UPDATE trucking_service
        SET
            company=?,
            contact=?,
            email=?,
            tel=?,
            type=?,
            base=?
        WHERE id=?
        """,

        (
            request.form["company"],
            request.form["contact"],
            request.form["email"],
            request.form["tel"],
            request.form["type"],
            request.form["base"],
            id
        )

    )

    conn.commit()

    return redirect(
        "/trucking_management"
    )

@app.route("/check_trucking")
def check_trucking():

    cursor.execute(
        "SELECT * FROM trucking_service"
    )

    return str(
        cursor.fetchall()
    )

@app.route("/check_courier")
def check_courier():
    cursor.execute("SELECT * FROM courier_service")
    return str(cursor.fetchall())

@app.route("/dashboard")
def dashboard():

    if "admin_logged_in" not in session:

        return redirect("/admin")
    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total_users = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE status='active'
        """
    )

    active_users = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE status='inactive'
        """
    )

    inactive_users = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM login_history
        """
    )

    login_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM sessions
        """
    )

    online_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM courier_service"
    )
    courier_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM customs_service"
    )
    customs_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM packing_service"
    )
    packing_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM cross_border_service"
    )
    cross_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM insurance_service"
    )
    insurance_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM trucking_service"
    )
    trucking_count = cursor.fetchone()[0]

    html = f"""

<html>

<head>

<style>

.body{{
    font-family:Arial,sans-serif;
    background:#f4f7fc;
    margin:0;
    padding:30px;
}}

.header{{
    background:linear-gradient(
        135deg,
        #0F95F5,
        #0056b3
    );

    color:white;

    padding:25px;

    border-radius:20px;

    margin-bottom:25px;

    box-shadow:
    0 4px 15px rgba(0,0,0,0.15);
}}

.header h1{{
    margin:0;
}}

.dashboard-grid{{
    display:grid;

    grid-template-columns:
    repeat(
        auto-fit,
        minmax(220px,1fr)
    );

    gap:20px;
}}

.card{{
    background:white;

    border-left:6px solid #0F95F5;

    border-radius:20px;

    padding:25px;

    text-align:center;

    box-shadow:
    0 4px 12px rgba(0,0,0,0.1);

    transition:0.3s;
}}

.card:hover{{
    transform:translateY(-5px);
}}

.card h2{{
    margin:0;
    font-size:18px;
    color:#666;
}}

.card h1{{
    margin-top:10px;
    color:#0F95F5;
}}

.menu{{
    margin-top:30px;
}}

.quick-grid{{

    display:grid;

    grid-template-columns:
    repeat(auto-fit,minmax(250px,1fr));

    gap:20px;

    margin-top:30px;
}}

.quick-card{{

    background:white;

    padding:25px;

    border-radius:20px;

    text-decoration:none;

    color:black;

    box-shadow:
    0 4px 12px rgba(0,0,0,0.1);

    transition:0.3s;
}}

.quick-card:hover{{

    transform:translateY(-5px);

    box-shadow:
    0 8px 20px rgba(0,0,0,0.15);
}}

.quick-title{{

    font-size:22px;

    font-weight:bold;

    margin-bottom:10px;
}}

.quick-desc{{

    color:#666;
}}

.menu a{{
    display:inline-block;

    margin-right:10px;

    padding:12px 18px;

    border-radius:10px;

    text-decoration:none;

    background:#0F95F5;

    color:white;
}}

</style>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

</head>

<body>

<div class="header">

    <h1>
    📊 LEO Logistics Dashboard
    </h1>

    <p>
    Business Solutions & New Ventures
    </p>

</div>

<div class="dashboard-grid">

    <div class="card">
        <h2>👥 Total Users</h2>
        <h1>{total_users}</h1>
    </div>

    <div class="card">
        <h2>🟢 Active Users</h2>
        <h1>{active_users}</h1>
    </div>

    <div class="card">
        <h2>🔴 Inactive Users</h2>
        <h1>{inactive_users}</h1>
    </div>

    <div class="card">
        <h2>📜 Login History</h2>
        <h1>{login_count}</h1>
    </div>

    <div class="card">
        <h2>👤 Current Login</h2>
        <h1>{online_users}</h1>
    </div>

    <div class="card">
        <h2>🚚 Courier</h2>
        <h1>{courier_count}</h1>
    </div>

    <div class="card">
        <h2>📄 Customs</h2>
        <h1>{customs_count}</h1>
    </div>

    <div class="card">
        <h2>📦 Packing</h2>
        <h1>{packing_count}</h1>
    </div>

    <div class="card">
        <h2>🌏 Cross Border</h2>
        <h1>{cross_count}</h1>
    </div>

    <div class="card">
        <h2>🛡 Insurance</h2>
        <h1>{insurance_count}</h1>
    </div>

    <div class="card">
        <h2>🚛 Trucking</h2>
        <h1>{trucking_count}</h1>
    </div>

    </div>

<div class="card">

    <h2>
    📊 Logistics Service Overview
    </h2>

    <canvas id="serviceChart"></canvas>

</div>

<h2>
⚡ Quick Access
</h2>

<div class="quick-grid">

<a href="/courier_management" class="quick-card">
    <div class="quick-title">🚚 Courier</div>
    <div class="quick-desc">
    Manage Courier Data
    </div>
</a>

<a href="/customs_management" class="quick-card">
    <div class="quick-title">📄 Customs</div>
    <div class="quick-desc">
    Manage Customs Data
    </div>
</a>

<a href="/packing_management" class="quick-card">
    <div class="quick-title">📦 Packing</div>
    <div class="quick-desc">
    Manage Packing Data
    </div>
</a>

<a href="/cross_management" class="quick-card">
    <div class="quick-title">🌏 Cross Border</div>
    <div class="quick-desc">
    Manage Cross Border Data
    </div>
</a>

<a href="/insurance_management" class="quick-card">
    <div class="quick-title">🛡 Insurance</div>
    <div class="quick-desc">
    Manage Insurance Data
    </div>
</a>

<a href="/trucking_management" class="quick-card">
    <div class="quick-title">🚛 Trucking</div>
    <div class="quick-desc">
    Manage Trucking Data
    </div>
</a>

</div>

<div class="menu">

    <a href="/admin">
    👥 User Management
    </a>

    <a href="/login_logs">
    📊 Login Logs
    </a>

    <a href="/login_history">
    📜 Login History
    </a>

</div>

<script>

const ctx =
document.getElementById(
'serviceChart'
);

new Chart(ctx, {{

    type: 'bar',

    data: {{

        labels: [

            'Courier',
            'Customs',
            'Packing',
            'Cross Border',
            'Insurance',
            'Trucking'

        ],

        datasets: [{{

            label:
            'Companies',

            data: [

                {courier_count},
                {customs_count},
                {packing_count},
                {cross_count},
                {insurance_count},
                {trucking_count}

            ],

            borderWidth: 1

        }}]

    }},

    options: {{

        responsive: true,

        plugins: {{

            legend: {{

                display: false

            }}

        }}

    }}

}});

</script>

</body>

</html>

"""

    return html

@app.route("/check_users")
def check_users():

    cursor.execute("""
    SELECT username,status
    FROM users
    """)

    return str(cursor.fetchall())

@app.route("/faq_category_management")
def faq_category_management():

    cursor.execute(
        """
        SELECT *
        FROM faq_categories
        ORDER BY category_name
        """
    )

    records = cursor.fetchall()

    html = """

    <h1>📂 FAQ CATEGORY MANAGEMENT</h1>

    <form
    method="POST"
    action="/add_category"
    >

    Category Name

    <br><br>

    <input name="category_name">

    <br><br>

    <button>
    ADD CATEGORY
    </button>

    </form>

    <hr>

    """

    for row in records:

        html += f"""

        <div
        style="
        border:1px solid #ddd;
        padding:15px;
        margin:10px;
        border-radius:10px;
        "
        >

        {row[1]}

        <br><br>

        <a href="/edit_category/{row[0]}">
        ✏️ EDIT
        </a>

        &nbsp;&nbsp;

        <a href="/delete_category/{row[0]}">
        🗑 DELETE
        </a>

        </div>

        """

    html += """

    <br>

    <a href="/admin">
    🔙 BACK
    </a>

    """

    return html

@app.route(
    "/add_category",
    methods=["POST"]
)
def add_category():

    category_name = request.form["category_name"]

    cursor.execute(

        """
        INSERT INTO faq_categories
        (
            category_name
        )
        VALUES
        (?)
        """,

        (
            category_name,
        )

    )

    conn.commit()

    return redirect(
        "/faq_category_management"
    )

@app.route("/edit_category/<int:id>")
def edit_category(id):

    cursor.execute(
        """
        SELECT *
        FROM faq_categories
        WHERE id=?
        """,
        (id,)
    )

    row = cursor.fetchone()

    return f"""

    <h1>Edit Category</h1>

    <form
    method="POST"
    action="/update_category/{id}"
    >

    <input
    name="category_name"
    value="{row[1]}"
    >

    <br><br>

    <button>
    SAVE
    </button>

    </form>

    """

@app.route(
    "/update_category/<int:id>",
    methods=["POST"]
)
def update_category(id):

    category_name = request.form["category_name"]

    cursor.execute(

        """
        UPDATE faq_categories
        SET category_name=?
        WHERE id=?
        """,

        (
            category_name,
            id
        )

    )

    conn.commit()

    return redirect(
        "/faq_category_management"
    )

@app.route("/delete_category/<int:id>")
def delete_category(id):

    cursor.execute(
        """
        DELETE FROM faq_categories
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()

    return redirect(
        "/faq_category_management"
    )

@app.route("/faq_management")
def faq_management():

    search = request.args.get(
        "search",
        ""
    )

    if search:

        cursor.execute(
            """
            SELECT rowid,*
            FROM faq
            WHERE lower(keyword) LIKE ?
            ORDER BY keyword
            """,
            (
                f"%{search.lower()}%",
            )
        )

    else:

        cursor.execute(
            """
            SELECT rowid,*
            FROM faq
            ORDER BY keyword
            """
        )

    records = cursor.fetchall()

    # โหลด Category จาก Database
    cursor.execute(
        """
        SELECT category_name
        FROM faq_categories
        ORDER BY category_name
        """
    )

    categories = cursor.fetchall()

    category_options = ""

    for category in categories:

        category_options += f"""
        <option value="{category[0]}">
        {category[0]}
        </option>
        """

    html = f"""

    <h1>📚 FAQ MANAGEMENT</h1>

    <form method="GET">

        <input
        name="search"
        placeholder="Search FAQ"
        style="
        width:300px;
        padding:8px;
        "
        >

        <button>
        🔍 Search
        </button>

    </form>

    <br>

    <form method="POST" action="/add_faq">

        Category

        <br>

        <select name="category">

        {category_options}

        </select>

        <br><br>

        Keyword

        <br>

        <input
        name="keyword"
        style="width:300px;"
        >

        <br><br>

        Answer

        <br>

        <textarea
        name="answer"
        rows="8"
        cols="60"
        ></textarea>

        <br><br>

        <button>
        SAVE
        </button>

    </form>

    <hr>

    """

    for row in records:

        html += f"""

        <div
        style="
        border:1px solid #ddd;
        padding:15px;
        margin:10px;
        border-radius:10px;
        "
        >

        <b>Category:</b> {row[1]}

        <br><br>

        <b>Keyword:</b> {row[2]}

        <br><br>

        {row[3]}

        <br><br>

        <a href="/edit_faq/{row[0]}">
        ✏️ EDIT
        </a>

        &nbsp;&nbsp;

        <a href="/delete_faq/{row[0]}">
        🗑 DELETE
        </a>

        </div>

        """

    html += """

    <br>

    <a href="/admin">
    🔙 BACK
    </a>

    """
 
    return html

@app.route("/check_category")
def check_category():

    cursor.execute(
        """
        SELECT *
        FROM faq_categories
        """
    )

    return str(cursor.fetchall())

@app.route("/create_default_categories")
def create_default_categories():

    categories = [

        "Customs",
        "Shipping",
        "Insurance",
        "Trucking",
        "Cross Border",
        "Warehouse",
        "General"

    ]

    for category in categories:

        cursor.execute(

            """
            INSERT INTO faq_categories
            (
                category_name
            )
            VALUES
            (?)
            """,

            (
                category,
            )

        )

    conn.commit()

    return "SUCCESS"

@app.route(
    "/add_faq",
    methods=["POST"]
)
def add_faq():

    category = request.form["category"]
    
    keyword = request.form["keyword"]

    answer = request.form["answer"]

    cursor.execute(

        """
        INSERT INTO faq
        (
            category,            
            keyword,
            answer
        )
        VALUES
        (?, ?, ?)
        """,

        (
            category,            
            keyword.lower(),
            answer
        )

    )

    conn.commit()

    return redirect(
        "/faq_management"
    )

@app.route("/delete_faq/<int:id>")
def delete_faq(id):

    cursor.execute(
        """
        DELETE FROM faq
        WHERE rowid=?
        """,
        (id,)
    )

    conn.commit()

    return redirect(
        "/faq_management"
    )

@app.route("/edit_faq/<int:id>")
def edit_faq(id):

    cursor.execute(
        """
        SELECT rowid,* 
        FROM faq
        WHERE rowid=?
        """,
        (id,)
    )

    row = cursor.fetchone()

    html = f"""

    <h1>✏️ EDIT FAQ</h1>

    <form
    method="POST"
    action="/update_faq/{id}"
    >

    Category

    <br>

    <input
    name="category"
    value="{row[1]}"
    >

    <br><br>
    Keyword

    <br>

    <input
    name="keyword"
    value="{row[2]}"
    style="width:400px;"
    >

    <br><br>

    Answer

    <br>

    <textarea
    name="answer"
    rows="10"
    cols="80"
    >{row[3]}</textarea>

    <br><br>

    <button>
    SAVE
    </button>

    </form>

    <br>

    <a href="/faq_management">
    🔙 BACK
    </a>

    """

    return html

@app.route(
    "/update_faq/<int:id>",
    methods=["POST"]
)
def update_faq(id):

    keyword = request.form["keyword"]

    answer = request.form["answer"]

    cursor.execute(

        """
        UPDATE faq
        SET
        category=?,
        keyword=?,
        answer=?
        WHERE rowid=?
        """,

        (
            category,
            keyword.lower(),
            answer,
            id
        )

    )

    conn.commit()

    return redirect(
        "/faq_management"
    )

@app.route("/update_faq_table")
def update_faq_table():

    try:

        cursor.execute(
            """
            ALTER TABLE faq
            ADD COLUMN category TEXT
            """
        )

        conn.commit()

        return "SUCCESS"

    except Exception as e:

        return str(e)

@app.route("/check_faq_table")
def check_faq_table():

    cursor.execute(
        "PRAGMA table_info(faq)"
    )

    return str(cursor.fetchall())

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

    if DEBUG_MODE:

        print(
            "CURRENT USER:",
            user_id
        )

    logged_in = False

    cursor.execute(
    "SELECT * FROM sessions WHERE user_id=?",
    (user_id,)
    )

    session_user = cursor.fetchone()

    if session_user:

        logged_in = True

        username = session_user[1]

        cursor.execute(
            """
            SELECT status
            FROM users
            WHERE username=?
            """,
            (username,)
        )

        user_status = cursor.fetchone()

        if (
            user_status
            and
            user_status[0] == "inactive"
        ):

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="⛔ บัญชีของคุณถูกระงับการใช้งาน"
                )
            )

            return

    if DEBUG_MODE:

        print(
            "LOGIN STATUS:",
            logged_in
        )

        # =========================
    # CHECK LOGIN
    # =========================

    if not logged_in:

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
                            "text": "🔐 กรุณา Login ก่อนใช้งาน",
                            "weight": "bold",
                            "size": "lg",
                            "wrap": True
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

                                "uri": f"https://liff.line.me/2010152202-xzzmHkWl?user_id={user_id}"

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
    # SEARCH COURIER
    # =========================

    if text.lower() == "courier":

        cursor.execute("""
        SELECT
        company,
        contact,
        email,
        tel
        FROM courier_service
        """)

        results = cursor.fetchall()

        reply = "🚚 COURIER\n\n"

        for row in results:

            reply += f"""
Company : {row[0]}
Contact : {row[1]}
E-mail : {row[2]}
Tel : {row[3]}

    """

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply[:5000])
        )

        return

    # =========================
    # SEARCH CUSTOMS
    # =========================

    if text.lower() == "customs":

        cursor.execute("""
        SELECT
        company,
        contact,
        email,
        tel,
        base
        FROM customs_service
        """)

        results = cursor.fetchall()

        reply = "📄 CUSTOMS\n\n"

        for row in results:

            reply += f"""
Company : {row[0]}
Contact : {row[1]}
Email : {row[2]}
Tel : {row[3]}
Base : {row[4]}

    """

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply[:5000])
        )

        return

    # =========================
    # SEARCH PACKING
    # =========================

    if text.lower() == "packing":

        cursor.execute("""
        SELECT
        company,
        contact,
        email,
        tel,
        service,
        base
        FROM packing_service
        """)

        results = cursor.fetchall()

        reply = "📦 PACKING\n\n"

        for row in results:

            reply += f"""
Company : {row[0]}
Contact : {row[1]}
Email : {row[2]}
Tel : {row[3]}
Service : {row[4]}
Base : {row[5]}
   
    """

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply[:5000])
        )

        return

    # =========================
    # SEARCH CROSS_BORDER
    # =========================

    if text.lower() == "cross border":

        cursor.execute("""
        SELECT
        company,
        contact,
        email,
        tel,
        route
        FROM cross_border_service
        """)

        results = cursor.fetchall()

        reply = "🌏 CROSS BORDER\n\n"

        for row in results:

            reply += f"""
Company : {row[0]}
Contact : {row[1]}
Email : {row[2]}
Tel : {row[3]}
Route : {row[4]}

    """

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply[:5000])
        )

        return

    # =========================
    # SEARCH INSURANCE
    # =========================

    if text.lower() == "insurance":

            cursor.execute("""
            SELECT
            company,
            department,
            contact,
            email,
            tel
            FROM insurance_service
            """
        )

        results = cursor.fetchall()

        reply = "🛡 INSURANCE\n\n"

        for row in results:

            reply += f"""
Company : {row[0]}
Department : {row[1]}
Contact : {row[2]}
E-mail : {row[3]}
Tel : {row[4]}

    """

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=reply[:5000]
            )
        )

        return

    # =========================
    # SEARCH TRUCKING
    # =========================

    if text.lower() == "trucking":

        cursor.execute("""
        SELECT
        company,
        contact,
        email,
        tel,
        type,
        base
        FROM trucking_service
        """)

        results = cursor.fetchall()

        reply = "🚛 TRUCKING\n\n"

        for row in results:

            reply += f"""
Company : {row[0]}
Contact : {row[1]}
Email : {row[2]}
Tel : {row[3]}
Type : {row[4]}
Base : {row[5]}

    """

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply[:5000])
        )

        return

    # =========================
    # ADMIN PANEL
    # =========================

    if text.lower() == "admin":

        line_bot_api.reply_message(

            event.reply_token,

            TextSendMessage(

                text="🔧 เปิดระบบจัดการ User",

                quick_reply={

                    "items":[

                        {
                            "type":"action",

                            "action":{

                                "type":"uri",

                                "label":"เปิด ADMIN",

                                "uri":"https://linebot-project-0qio.onrender.com/admin"

                            }
  
                        }

                    ]

                }

            )

        )

        return

    # =========================
    # MENU
    # =========================

    if "menu" in text.lower():

        reply = (
            "📋 MENU\n\n"
            "1. trucking\n"
            "2. customs\n"
            "3. insurance\n"
            "4. packing\n"
            "5. cross border\n"
            "6. courier"
        )

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

        return

    # =========================
    # CUSTOMS
    # =========================

    if "customs" in text.lower():

        cursor.execute(
            """
            SELECT
            company,
            contact,
            email,
            tel,
            base
            FROM customs_service
            """
        )

        records = cursor.fetchall()

        if results:

            for row in records:

                reply += f"""
        📄 {row[0]}
        👤 {row[1]}
        📧 {row[2]}
        📞 {row[3]}
        📍 {row[4]}

        ----------------
        """

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=reply[:5000]
                )
            )

            return

    # =========================
    # COURIER
    # =========================

    if "courier" in text.lower():

        cursor.execute(
            """
            SELECT
            company,
            contact,
            email,
            tel
            FROM courier_service
            """
        )

        records = cursor.fetchall()

        if results:

            for row in records:

                reply += f"""
        🚚 {row[0]}
        👤 {row[1]}
        📧 {row[2]}
        📞 {row[3]}

        -------------------
        """

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=reply[:5000]
                )
            )

            return

    # =========================
    # CROSS BORDER
    # =========================

    if "cross border" in text.lower():

        replies = []

        for index, row in cross_df.iterrows():

            text_data = ""

            for col in cross_df.columns:

                if "Unnamed" not in str(col) and pd.notna(row[col]):

                    text_data += f"{col}: {row[col]}\n"

            replies.append(text_data)

        reply = "\n-----------------\n".join(replies)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply[:5000])
        )

        return


    # =========================
    # PACKING
    # =========================

    if "packing" in text.lower():

        replies = []

        for index, row in packing_df.iterrows():

            text_data = ""

            for col in packing_df.columns:

                if "Unnamed" not in str(col) and pd.notna(row[col]):

                    text_data += f"{col}: {row[col]}\n"

            replies.append(text_data)

        reply = "\n-----------------\n".join(replies)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply[:5000])
        )

        return


    # =========================
    # INSURANCE
    # =========================

    if "insurance" in text.lower():

        replies = []

        for index, row in insurance_df.iterrows():

            text_data = ""

            for col in insurance_df.columns:

                if "Unnamed" not in str(col) and pd.notna(row[col]):

                    text_data += f"{col}: {row[col]}\n"

            replies.append(text_data)

        reply = "\n-----------------\n".join(replies)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply[:5000])
        )

        return


    # =========================
    # TRUCKING
    # =========================

    if "trucking" in text.lower():

        replies = []

        for index, row in reefer_df.iterrows():

            text_data = ""

            for col in reefer_df.columns:

                if "Unnamed" not in str(col) and pd.notna(row[col]):

                    text_data += f"{col}: {row[col]}\n"

            replies.append(text_data)

        reply = "\n-----------------\n".join(replies)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply[:5000])
        )

        return

    # =========================
    # LOGOUT
    # =========================

    if "logout" in text.lower():

        cursor.execute(
            "DELETE FROM sessions WHERE user_id=?",
            (user_id,)
        )

        conn.commit()

        reply = "✅ Logout สำเร็จ"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

        return

    search_reply = ""
    found = False

    # COURIER

    cursor.execute(
        """
        SELECT company, contact, Email, Tel
        FROM courier_service
        WHERE lower(company) LIKE ?
        """,
        (
            f"%{text.lower()}%",
        )
    )

    results = cursor.fetchall()

    if results:

        found = True

        search_reply += "\n🚚 COURIER\n"

        for row in results:

            search_reply += f"""
Company : {row[0]}
Contact : {row[1]}
E-mail : {row[2]}
Tel : {row[3]}

    """

    # CUSTOMS

    cursor.execute(
        """
        SELECT company, contact, Email, Tel, Base
        FROM customs_service
        WHERE lower(company) LIKE ?
        """,
        (
            f"%{text.lower()}%",
        )
    )

    results = cursor.fetchall()

    if results:

        found = True

        search_reply += "\n📄 CUSTOMS\n"

        for row in results:

            search_reply += f"""
Company : {row[0]}
Contact : {row[1]}
Email : {row[2]}
Tel : {row[3]}
Base : {row[4]}

    """

    # PACKING

    cursor.execute(
        """
        SELECT company, contact, Email, Tel, Service, Base
        FROM packing_service
        WHERE lower(company) LIKE ?
        """,
        (
            f"%{text.lower()}%",
        )
    )

    results = cursor.fetchall()

    if results:

        found = True

        search_reply += "\n📦 PACKING\n"

        for row in results:

            search_reply += f"""
Company : {row[0]}
Contact : {row[1]}
Email : {row[2]}
Tel : {row[3]}
Service : {row[4]}
Base : {row[5]}

    """

    # CROSS BORDER

    cursor.execute(
        """
        SELECT company, contact, Email, Tel, Route
        FROM cross_border_service
        WHERE lower(company) LIKE ?
        """,
        (
            f"%{text.lower()}%",
        )
    )

    results = cursor.fetchall()

    if results:

        found = True

        search_reply += "\n🌏 CROSS BORDER\n"

        for row in results:

            search_reply += f"""
Company : {row[0]}
Contact : {row[1]}
Email : {row[2]}
Tel : {row[3]}
Route : {row[4]}

    """

    # INSURANCE

    cursor.execute(
        """
        SELECT company, contact, Email, Tel
        FROM insurance_service
        WHERE lower(company) LIKE ?
        """,
        (
            f"%{text.lower()}%",
        )
    )

    results = cursor.fetchall()

    if results:

        found = True

        search_reply += "\n🛡 INSURANCE\n"

        for row in results:

            search_reply += f"""
Company : {row[0]}
Contact : {row[2]}
E-mail : {row[3]}
Tel : {row[4]}

    """

    # TRUCKING

    cursor.execute(
        """
        SELECT company, contact, Email, Tel, Type, Base
        FROM trucking_service
        WHERE lower(company) LIKE ?
        """,
        (
            f"%{text.lower()}%",
        )
    )

    results = cursor.fetchall()

    if results:

        found = True

        search_reply += "\n🚛 TRUCKING\n"

        for row in results:

            search_reply += f"""
Company : {row[0]}
Contact : {row[1]}
Email : {row[2]}
Tel : {row[3]}
Type : {row[4]}
Base : {row[5]}
  
    """

    if found:

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=search_reply[:5000]
            )
        )

        return

    # =========================
    # FAQ
    # =========================

    cursor.execute(

        """
        SELECT answer
        FROM faq
        WHERE lower(keyword)=?
        """,

        (
            text.lower(),
        )

    )

    faq = cursor.fetchone()

    if faq:

        line_bot_api.reply_message(

            event.reply_token,

            TextSendMessage(
                text=faq[0]
            )

        )

        return

    # =========================
    # DEFAULT
    # =========================

    else:

        reply = "พิมพ์ menu เพื่อดูเมนู"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

        return


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)