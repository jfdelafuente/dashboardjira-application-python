"""
pytest fixtures for testing.

Provides:
    - app: Flask application instance with testing config
    - client: Flask test client for HTTP requests
    - db: Database instance
    - init_database: Initialize database with test data
"""

import pytest
from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    """
    Create Flask application instance for testing.

    Scope: session (created once per test session)

    Returns:
        Flask application configured for testing
    """
    app = create_app("testing")

    # Establish application context
    ctx = app.app_context()
    ctx.push()

    yield app

    # Cleanup
    ctx.pop()


@pytest.fixture(scope="session")
def db(app):
    """
    Create database instance for testing.

    Scope: session (created once per test session)

    Args:
        app: Flask application fixture

    Returns:
        SQLAlchemy database instance
    """
    # Create all tables
    _db.create_all()

    yield _db

    # Cleanup
    _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """
    Create Flask test client.

    Scope: function (new client for each test)

    Args:
        app: Flask application fixture

    Returns:
        Flask test client for making HTTP requests
    """
    return app.test_client()


@pytest.fixture(scope="function")
def init_database(db):
    """
    Initialize database with test data.

    Scope: function (reset database for each test)

    Args:
        db: Database fixture

    Yields:
        Database with test data

    Cleanup:
        Removes all data after test
    """
    # Create test data (will be implemented in user story tests)
    # For now, just ensure clean state
    yield db

    # Cleanup: remove all data after test
    db.session.remove()
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
