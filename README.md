# Plane-n-Simple ✈️

Plane-n-Simple is a Streamlit web application that helps users **find airports** and **search for flights** easily. The app features an interactive map of global airports and a simple interface for searching flights and managing user profiles.

## 🚀 Live Deployment

[Click here to access our live deployed website!](https://plane-n-simple-team3-func.streamlit.app/)

## 📁 Project Structure

```bash
├── app.py                 # Main entry point with sidebar navigation
├── home.py                # Home page with airport map
├── flight_search.py       # Flight search interface
├── profile_page.py        # User profile page
├── airports.csv           # CSV file with airport data
├── requirements.txt       # Python dependencies
└── web_images/            # Banner and other static images
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/2003antonio/plane-n-simple-team3.git
cd plane-n-simple
```

### 2. Set Up a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

## Features Right Now

- **Interactive Map**: View supported airports with Pydeck.
- **Flight Search**: Enter departure, destination, and date to simulate flight search.
- **User Profile**: Input personal details and upload a profile picture.

## For Team 3

- Each major component lives in its own module (`home.py`, `flight_search.py`, `profile_page.py`)
- Add your feature as a new module and link it in `app.py`
- Push updates to your own branch for code review
- Please try to keep the UI elements clean and consistent with Streamlit’s component style

---
