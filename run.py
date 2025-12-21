"""
Application entry point.

Runs the Flask development server.

Usage:
    python run.py                 # Run with default config (development)
    FLASK_ENV=production python run.py  # Run in production mode
"""

from app import create_app

# Create application instance
app = create_app()

if __name__ == "__main__":
    # Run development server
    # In production, use Gunicorn instead: gunicorn -w 4 run:app
    app.run(debug=True, host="0.0.0.0", port=5000)
