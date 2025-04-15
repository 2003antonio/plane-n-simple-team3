# Plane-n-Simple ✈️

Plane-n-Simple is a Streamlit web application that helps users **find airports**, **search for flights**, and manage their profiles. The app features an interactive map, simulated flight search, and Points of Interest (POI) integration.

## 🚀 Live Deployment

[Click here to access our live deployed website!](https://plane-n-simple-team3-func.streamlit.app/)

## 📁 Project Structure

```bash
├── app.py                 # Main entry point with sidebar navigation
├── home.py                # Home page with airport map
├── flight_search.py       # Flight search interface
├── poi_search.py          # POI search using Geoapify or Amadeus
├── profile_page.py        # User profile management
├── admin_page.py          # Admin-specific functionality
├── airports.csv           # Airport data for mapping
├── requirements.txt       # Python dependencies
├── README.md              # Project overview and setup
└── web_images/            # Static images for UI
```

## 🔐 Required Configuration

Before running the app, create a file at `.streamlit/secrets.toml` and insert your API keys and credentials:

```toml
[firebase]
type = "service_account"
project_id = "insert_your_project_id"
private_key_id = "insert_your_private_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\nINSERT_YOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "insert_your_client_email"
client_id = "insert_your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "insert_your_client_x509_cert_url"
databaseURL = "insert_your_firebase_database_url"
apiKey = "insert_your_firebase_api_key"
authDomain = "insert_your_auth_domain"
appId = "insert_your_app_id"

[amadeus]
client_id = "insert_your_amadeus_client_id"
client_secret = "insert_your_amadeus_client_secret"

[geoapify]
api_key = "insert_your_geoapify_api_key"
```

> **Never commit secrets to GitHub.** The `.gitignore` file is already configured to exclude this file.

## 🛠 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/2003antonio/plane-n-simple-team3.git
cd plane-n-simple
```

### 2. Add Your Streamlit Secrets

Create a file at `.streamlit/secrets.toml` and configure it as shown above.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

## ✨ Features

- **Interactive Map**: View supported U.S. airports using Pydeck.
- **Flight Search**: Enter origin, destination, and date to simulate flight results.
- **POI Search**: Find nearby places of interest using Amadeus or Geoapify APIs.
- **User Authentication**: Firebase-based login and sign-up.
- **User Profiles**: Manage personal information (profile image optional).
- **Admin Tools**: Placeholder for advanced admin features.

## 🧑‍💻 For Team 3 Developers

- Keep each feature in its own Python module.
- Add new pages and link them in `app.py` navigation.
- Use clean, consistent UI components.
- Commit to your branch and request code reviews before merging.

---
