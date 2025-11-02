# Viddy Downloader 2.0

Viddy Downloader is a full-featured video downloader web app with user authentication, subscriptions, feedback, and an admin dashboard — built with Flask.

## Features
- Download from major platforms (YouTube, Instagram, TikTok, Twitter/X, Facebook, Reddit, and more)
- Login/Signup with session management
- Subscription tiers (Free, Basic, Premium)
- Feedback submission and admin responses
- Admin dashboard for users, downloads, subscriptions, and feedback

## Setup
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies: `pip install -r requirements.txt`.
3. Run locally: `python app.py` (or `py -3 app.py` on Windows).

Admin user is auto-created at first run:
- Email: `admin@viddydownloader.com`
- Password: `admin123` (change in production)

## Deploy (Render)
Render can run this app with the included `Procfile`:
- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

Ensure environment variables are set as needed (e.g., `SECRET_KEY`).

## Project Structure
- `app.py` — Flask app entrypoint
- `models.py` — SQLAlchemy models
- `auth.py` — authentication routes
- `subscription.py` — subscription/payment routes
- `admin.py` — admin routes and dashboard
- `feedback.py` — feedback routes
- `templates/` — HTML templates
- `requirements.txt` — dependencies