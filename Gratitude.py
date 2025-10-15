import streamlit as st
from pymongo import MongoClient
import datetime
import requests

# -----------------------------
# 🌸 CONFIG & CONNECTION
# -----------------------------
st.set_page_config(page_title="🌼 My Gratitude Journal", page_icon="🌸", layout="centered")

MONGO_URI = "mongodb+srv://deenbandhusingh335_db_user:Ev4EiJTa9P9OPPMx@cluster0.y4umx0s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Change this to your Atlas URI
client = MongoClient(MONGO_URI)
db = client["gratitude_journal"]
users_collection = db["users"]
entries_collection = db["entries"]

# -----------------------------
# 🌤 GET DAILY QUOTE FROM API
# -----------------------------
def get_daily_quote():
    try:
        res = requests.get("https://zenquotes.io/api/today")
        data = res.json()
        quote = f"“{data[0]['q']}” — *{data[0]['a']}*"
        return quote
    except Exception:
        return "“Start your day with gratitude and a smile 🌞”"

# -----------------------------
# 🌸 PAGE STYLE
# -----------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #fff0f5, #fffafc);
        color: #444;
        font-family: "Comic Sans MS", cursive, sans-serif;
    }
    h1, h2, h3, h4 {
        text-align: center;
        color: #d63384;
    }
    .entry-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# 🌸 AUTH FUNCTIONS
# -----------------------------
def signup(username, password):
    if users_collection.find_one({"username": username}):
        return False, "Username already exists."
    users_collection.insert_one({"username": username, "password": password})
    return True, "Signup successful! Please log in."

def login(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return True
    return False

# -----------------------------
# 🌸 APP LOGIC
# -----------------------------
st.markdown("<h1>🌼 My Daily Gratitude Journal 🌸</h1>", unsafe_allow_html=True)

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Select Option", menu)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if choice == "Sign Up":
    st.subheader("Create a New Account 🌸")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        success, message = signup(new_user, new_pass)
        if success:
            st.success(message)
        else:
            st.error(message)

elif choice == "Login":
    st.subheader("Login to Your Journal 💖")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome back, {username}! 🌸")
        else:
            st.error("Invalid username or password ❌")

# -----------------------------
# 🌿 MAIN JOURNAL PAGE
# -----------------------------
if st.session_state.logged_in:
    st.write("---")
    quote = get_daily_quote()
    st.markdown(f"<h4>{quote}</h4>", unsafe_allow_html=True)
    st.write("---")

    today = datetime.date.today().strftime("%B %d, %Y")
    st.subheader(f"💖 What are 3 things you’re thankful for today? ({today})")

    col1, col2, col3 = st.columns(3)
    with col1:
        gratitude1 = st.text_input("1️⃣ First thing")
    with col2:
        gratitude2 = st.text_input("2️⃣ Second thing")
    with col3:
        gratitude3 = st.text_input("3️⃣ Third thing")

    if st.button("💾 Save My Gratitude"):
        entries = [gratitude1.strip(), gratitude2.strip(), gratitude3.strip()]
        if all(entries):
            data = {
                "username": st.session_state.username,
                "date": today,
                "entries": entries,
                "timestamp": datetime.datetime.now()
            }
            entries_collection.insert_one(data)
            st.success("🌻 Your gratitude has been saved successfully!")
        else:
            st.warning("Please fill in all three gratitude points 🌼")

    # -----------------------------
    # 📅 FILTER BY DATE
    # -----------------------------
    st.write("---")
    st.subheader("📅 View Your Gratitude by Date")
    all_dates = [entry["date"] for entry in entries_collection.find(
        {"username": st.session_state.username})]
    all_dates = sorted(list(set(all_dates)))

    if all_dates:
        selected_date = st.selectbox("Select a date to view:", all_dates)
        entries = list(entries_collection.find(
            {"username": st.session_state.username, "date": selected_date}).sort("timestamp", -1))
        for record in entries:
            st.markdown(
                f"<div class='entry-box'><b>🌸 {record['date']}</b><br>"
                + "<br>".join([f"• {item}" for item in record['entries']])
                + "</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No entries found yet. Start journaling today 🌸")

    st.write("---")
    st.markdown("<p style='text-align:center;'>Made with 💖 and positivity ✨</p>", unsafe_allow_html=True)
