import os
import sqlite3
import joblib
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Database Initialization
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Load Trained Model and Vectorizer
model = joblib.load("models/phishing_model.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")

# Telegram Bot Configuration (Optional: update with your own token and chat id if needed)
TELEGRAM_BOT_TOKEN = "8944543732:AAHopFo3J25ohtv6B4ZyGoLiduaRe9KVdC8"
TELEGRAM_CHAT_ID = "8888082571"

def send_telegram_alert(input_text, confidence):
    """Sends an alert to Telegram if a high-risk phishing vector is found."""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        return  # Skip if token isn't configured yet
    
    message = (
        f"🚨 **HIGH-RISK PHISHING DETECTED!** 🚨\n\n"
        f"**Input:** {input_text}\n"
        f"**Threat Probability:** {confidence * 100:.2f}%\n"
        f"**Action:** Analyzed and flagged by AI Security System."
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        user_input = request.form.get("user_input")
        
        if user_input:
            # Transform input using the vectorizer and predict
            transformed_input = vectorizer.transform([user_input])
            prediction = model.predict(transformed_input)[0]
            probabilities = model.predict_proba(transformed_input)[0]
            
            # Probability of being malicious (Class 1)
            malicious_prob = probabilities[1] if len(probabilities) > 1 else float(prediction)
            
            is_phishing = bool(prediction == 1 or malicious_prob > 0.5)
            status_text = "Malicious / Phishing" if is_phishing else "Safe / Legitimate"
            
            result = {
                "input": user_input,
                "status": status_text,
                "confidence": round(malicious_prob * 100, 2),
                "risk": "High Risk" if is_phishing else "Low Risk"
            }
            
            # Save scan results to SQLite database
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO scan_history (url, result) VALUES (?, ?)", 
                    (user_input, status_text)
                )
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Database Error: {e}")
            
            # Trigger Telegram alert if malicious
            if is_phishing:
                send_telegram_alert(user_input, malicious_prob)

    # Fetch scan history from database to display on UI
    history = []
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT url, result, timestamp FROM scan_history ORDER BY id DESC")
        history = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Fetch History Error: {e}")

    return render_template("index.html", result=result, history=history)

if __name__ == "__main__":
    app.run(debug=True, port=5000)