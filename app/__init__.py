"""
Flask application factory.

Creates and configures the Flask application instance with:
- Database initialization (SQLAlchemy)
- Migration support (Flask-Migrate)
- Blueprint registration
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions (without app context)
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str = None) -> Flask:
    """
    Application factory pattern.

    Creates and configures a Flask application instance.

    Args:
        config_name: Configuration to use (development, testing, production).
                    If None, uses FLASK_ENV environment variable or 'development'.

    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)

    # Determine configuration
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    # Load configuration
    from app.config import get_config

    app.config.from_object(get_config(config_name))

    # Initialize extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate can detect them
    from app.models import Issue, TeamMember

    # Register blueprints
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.api import bp as api_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
