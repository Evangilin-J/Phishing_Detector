import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 1. Sample Dataset (URLs & Email Body Content)
data = [
    # Phishing / Malicious samples (Label: 1)
    ("http://login-security-verify-account-update.com", 1),
    ("http://paypal-verification-alert-user-login.net", 1),
    ("http://bankofamerica-secure-update-login.org", 1),
    ("http://claim-free-iphone-giftcard-now.xyz", 1),
    ("http://account-suspended-verify-identity-today.info", 1),
    ("Urgent: Your account is suspended. Click here to verify credentials now!", 1),
    ("Security Alert: Unauthorized login attempt detected. Login immediately to secure account.", 1),
    
    # Legitimate / Safe samples (Label: 0)
    ("https://www.google.com", 0),
    ("https://github.com/login", 0),
    ("https://www.amazon.com/dp/B08N5WRWNW", 0),
    ("https://developer.mozilla.org/en-US/docs/Web", 0),
    ("https://www.wikipedia.org", 0),
    ("Here is the monthly project update report attached for your review.", 0),
    ("Thanks for meeting today! Let's follow up on Monday morning.", 0)
]

texts, labels = zip(*data)

# 2. Feature Extraction using TF-IDF Vectorizer
vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
X = vectorizer.fit_transform(texts)
y = labels

# 3. Train Machine Learning Model (Random Forest)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 4. Evaluate Model
predictions = model.predict(X_test)
print(f"Model Training Accuracy: {accuracy_score(y_test, predictions) * 100:.2f}%")

# 5. Save Model & Vectorizer to 'models' folder
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/phishing_model.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")

print("Model and Vectorizer saved successfully in the 'models/' directory!")