"""
Flask application configuration.

Defines configuration classes for different environments:
- DevelopmentConfig: Local development with SQLite
- TestingConfig: Testing with in-memory SQLite
- ProductionConfig: Production with PostgreSQL
"""

import os
from typing import Type


class Config:
    """Base configuration with common settings."""

    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Jira integration
    JIRA_SERVER = os.getenv("JIRA_SERVER", "https://your-company.atlassian.net")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "SUPPORT")

    # Mock data mode (for testing without Jira)
    USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "False").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration using SQLite."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dashboard.db")
    SQLALCHEMY_ECHO = True  # Log SQL queries in development


class TestingConfig(Config):
    """Testing configuration using in-memory SQLite."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    USE_MOCK_DATA = True  # Always use mock data in tests


class ProductionConfig(Config):
    """Production configuration using PostgreSQL."""

    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://localhost/support_dashboard"
    )


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: str = "default") -> Type[Config]:
    """
    Get configuration class by name.

    Args:
        config_name: Name of configuration (development, testing, production, default)

    Returns:
        Configuration class

    Raises:
        KeyError: If config_name is not valid
    """
    return config[config_name]
