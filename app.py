import os
from flask import Flask, request, render_template, redirect, session
import os

from dotenv import load_dotenv
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from datetime import datetime
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
    password TEXT
)
""")

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
        "SELECT username FROM users"
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

    <a href="/admin_logout">
    🚪 LOGOUT
    </a>

    <a href="/login_logs">
    📊 LOGIN LOGS
    </a>

    <a href="/login_history">
    📜 LOGIN HISTORY
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

        html += f"""

        <div class="user-card">

            <h3>
            👤 {user[0]}
            </h3>

            <br>

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
                    VALUES (?, ?)
                    """,

                    (
                        username,
                        hashed_password
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

    # =========================
    # CUSTOMS
    # =========================

    elif filename == "customs_clearance.xlsx":

        customs_df = pd.read_excel(
            "customs_clearance.xlsx"
        )

    # =========================
    # PACKING
    # =========================

    elif filename == "packing.xlsx":

        packing_df = pd.read_excel(
            "packing.xlsx"
        )

    # =========================
    # CROSS BORDER
    # =========================

    elif filename == "cross_border.xlsx":

        cross_df = pd.read_excel(
            "cross_border.xlsx"
        )

    # =========================
    # INSURANCE
    # =========================

    elif filename == "cargo_insurance.xlsx":

        insurance_df = pd.read_excel(
            "cargo_insurance.xlsx"
        )

    # =========================
    # TRUCKING
    # =========================

    elif filename == "tracking_reefer.xlsx":

        reefer_df = pd.read_excel(
            "tracking_reefer.xlsx"
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
        VALUES (?, ?)
        """,

        (
            username,
            hashed_password
        )
    )

    conn.commit()

    return redirect("/admin")

# =========================
# DELETE USER
# =========================

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

    return f"""

    <h2>
    ✅ RESET PASSWORD SUCCESS
    </h2>

    <p>

    USER:
    {username}

    </p>

    <p>

    NEW PASSWORD:
    1234

    </p>

    <a href="/admin">
    🔙 BACK
    </a>

    """

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
            VALUES (?, ?)
            """,

            (
                username,
                hashed_password
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
        #0F95F5,
        #5B9BF0
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

    background:#f8f9ff;

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

    background:#79D1FC;

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

        replies = []

        for index, row in customs_df.iterrows():

            text_data = ""

            for col in customs_df.columns:

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
    # COURIER
    # =========================

    if "courier" in text.lower():

        replies = []

        for index, row in courier_df.iterrows():

            text_data = ""

            for col in courier_df.columns:

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