import streamlit as st
import pickle
import string
import sqlite3
import pandas as pd

from datetime import datetime

from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Email Spam Filter",
    layout="wide"
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users(
username TEXT,
password TEXT
)
''')

# ---------------- NLTK ----------------
@st.cache_resource
def load_nltk():
    nltk.download('punkt_tab')
    nltk.download('stopwords')

load_nltk()

ps = PorterStemmer()

# ---------------- TEXT PROCESSING ----------------
def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []

    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stopwords.words("english") and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)

# ---------------- LOAD MODEL ----------------
tfidf = pickle.load(open('vectorizer.pkl', 'rb'))
model = pickle.load(open('model.pkl', 'rb'))

# ---------------- SESSION ----------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- CSS ----------------
st.markdown("""
<style>

.main {
    background: linear-gradient(to right, #e8ebff, #f4f5ff);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #00c9a7, #00b4d8);
    width: 220px !important;
}

/* Remove large white spaces */
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* INPUT FIELD FIX */
.stTextInput > div > div > input {
    background-color: white !important;
    color: black !important;
    caret-color: black !important;

    height: 48px !important;
    font-size: 18px !important;

    border-radius: 10px !important;
    padding-left: 12px !important;
}

/* PASSWORD FIELD */
.stTextInput input[type="password"] {
    caret-color: black !important;
}

.main-card {
    background: rgba(255,255,255,0.18);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.05);
    text-align: center;
    margin-top: 10px;
    width: 80%;
    margin-left: auto;
    margin-right: auto;
}

/* Title */
.title {
    font-size: 70px;
    font-weight: bold;
    color: #00a896;
}

/* Subtitle */
.subtitle {
    font-size: 25px;
    color: #00a896;
    margin-top: 10px;
}

/* Inputs */
input, textarea {
    border-radius: 12px !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    height: 50px;
    border: none;
    border-radius: 10px;
    background: linear-gradient(to right, #4f8cff, #5a67ff);
    color: white;
    font-size: 18px;
}

/* Result */
.spam {
    color: red;
    font-size: 40px;
    font-weight: bold;
}

.ham {
    color: green;
    font-size: 40px;
    font-weight: bold;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

.login-card{
    background: rgba(255,255,255,0.35);
    padding: 35px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}

.login-title{
    text-align:center;
    color:#00a896;
    font-size:40px;
    font-weight:bold;
    margin-bottom:20px;
}

div.stButton > button{
    width:100%;
    height:50px;
    border:none;
    border-radius:8px;
    background:linear-gradient(90deg,#4f8cff,#5a67ff);
    color:white;
    font-size:18px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/1041/1041916.png",
    width=150
)

# =========================================================
# LOGIN / REGISTER
# =========================================================

if st.session_state.logged_in == False:

    menu = st.sidebar.radio(
        "Menu",
        ["Home", "Login", "Register"]
    )

    # ---------------- HOME ----------------
    if menu == "Home":

        st.markdown("""
        <div class="main-card">
            <div class="title">Intelligent Email Spam Filter</div>
            <div class="subtitle">
            Say goodbye to spam overload!
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- REGISTER ----------------
    # ---------------- REGISTER ----------------
    elif menu == "Register":

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:

            st.markdown("""
            <style>

            .register-box{
                background: rgba(255,255,255,0.25);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0px 0px 15px rgba(0,0,0,0.08);
                margin-top: 60px;
            }

            .register-title{
                text-align:center;
                font-size:45px;
                font-weight:bold;
                color:#00a896;
                margin-bottom:30px;
            }

            div.stButton > button{
                width:100%;
                height:50px;
                border:none;
                border-radius:10px;
                background: linear-gradient(to right,#4f8cff,#5a67ff);
                color:white;
                font-size:20px;
                font-weight:bold;
            }

            </style>
            """, unsafe_allow_html=True)

            st.markdown(
                "<h1 style='text-align:center; color:#00a896;'>Register</h1>",
                unsafe_allow_html=True
            )

            new_user = st.text_input("Create Username")

            new_pass = st.text_input(
                "Create Password",
                type="password"
            )

            confirm_pass = st.text_input(
                "Confirm Password",
                type="password"
            )

            if st.button("Register"):

                # Empty fields check
                if new_user == "" or new_pass == "" or confirm_pass == "":
                    st.warning("Please fill all fields")

                # Password match check
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match")

                else:

                    # Check existing user
                    c.execute(
                        "SELECT * FROM users WHERE username=?",
                        (new_user,)
                    )

                    existing_user = c.fetchone()

                    if existing_user:
                        st.warning("Username already exists")

                    else:

                        c.execute(
                            "INSERT INTO users VALUES (?,?)",
                            (new_user, new_pass)
                        )

                        conn.commit()

                        st.success("Account Created Successfully!")
    # ---------------- LOGIN ----------------
    elif menu == "Login":

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:

            st.markdown('<div class="login-box">', unsafe_allow_html=True)

            st.markdown("""
            <div class="login-title">
                Login
            </div>
            """, unsafe_allow_html=True)

            username = st.text_input("Username")

            password = st.text_input(
                "Password",
                type="password"
            )

            if st.button("Login"):

             c.execute(
                       "SELECT * FROM users WHERE username=? AND password=?",
                        (username, password)
    )

    data = c.fetchone()

    st.success("Login Successful!")

    st.rerun()

         else:

               st.error("Invalid Username or Password")

                st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- REGISTER ----------------
    elif menu == "Register":


        new_user = st.text_input("Create Username")

        new_pass = st.text_input(
            "Create Password",
            type="password"
        )

        if st.button("Register"):

            c.execute(
                "INSERT INTO users VALUES (?,?)",
                (new_user, new_pass)
            )

            conn.commit()

            st.success("Registered Successfully")


# =========================================================
# AFTER LOGIN
# =========================================================

else:

    menu = st.sidebar.radio(
        "Menu",
      ["Check by Message", "History", "Logout"]
    )

    st.sidebar.success(
        f"Welcome {st.session_state.username}"
    )

    # ---------------- CHECK MESSAGE ----------------
    # ---------------- CHECK MESSAGE ----------------
    # ---------------- CHECK MESSAGE ----------------
    if menu == "Check by Message":

        st.markdown("""
        <h1 style='
            text-align:center;
            color:#00a896;
            font-size:55px;
        '>
            Email Spam Classifier
        </h1>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2.5, 1])

        with col2:

            input_sms = st.text_area(
                "Enter your message",
                height=200
            )

            predict_btn = st.button("Predict")
            if predict_btn:

                transformed_sms = transform_text(input_sms)

                vector_input = tfidf.transform([transformed_sms])

                result = model.predict(vector_input)[0]

                probability = model.predict_proba(vector_input)

                if result == 1:
                    confidence = probability[0][1] * 100
                else:
                    confidence = probability[0][0] * 100



                # SAVE HISTORY
                st.session_state.history.append({
                    "Message": input_sms,
                    "Result": "Spam" if result == 1 else "Not Spam",
                    "Confidence": f"{confidence:.2f}%",
                    "Time": datetime.now().strftime("%H:%M:%S")
                })

                # RESULT
                if result == 1:

                    st.markdown("""
                    <h2 style='
                        text-align:Left;
                        color:red;
                        margin-top:10px;
                    '>
                        🚫 Spam
                    </h2>
                    """, unsafe_allow_html=True)

                else:

                    st.markdown("""
                    <h2 style='
                        text-align:Left;
                        color:green;
                        margin-top:10px;
                    '>
                        ✅ Not Spam
                    </h2>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <h4 style='text-align:Left;color:#333;'>
                    Confidence: {confidence:.2f}%
                </h4>
                """, unsafe_allow_html=True)
    # ---------------- LOGOUT ----------------
    elif menu == "Logout":

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()
    # ---------------- DASHBOARD ----------------

    # ---------------- HISTORY ----------------
    elif menu == "History":

        st.markdown("""
        <h1 style='
            text-align:center;
            color:#00a896;
            font-size:50px;
        '>
            Prediction History
        </h1>
        """, unsafe_allow_html=True)

        # CLEAR ALL BUTTON
        if st.button("Clear All History"):
            st.session_state.history = []

            st.success("History Cleared Successfully")

            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # HISTORY ITEMS
        if st.session_state.history:
            for index, item in enumerate(reversed(st.session_state.history)):

                with st.container(border=True):

                    st.write("📧 Message:", item["Message"])
                    st.write("📌 Result:", item["Result"])
                    st.write("🎯 Confidence:", item["Confidence"])
                    st.write("🕒 Time:", item["Time"])

                    if st.button("🗑 Delete", key=index):
                        original_index = len(st.session_state.history) - 1 - index
                        st.session_state.history.pop(original_index)
                        st.rerun()

                st.divider()


        else:

            st.info("No history available")

