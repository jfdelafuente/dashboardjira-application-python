"""
Unit tests for Pagination helper.

Tests:
    - calculate_pagination() returns correct page metadata
    - Handles edge cases (0 items, 1 item, exact page boundary)
"""

import pytest
from app.utils.pagination import calculate_pagination


class TestPaginationHelper:
    """Test pagination calculation logic."""

    def test_calculate_pagination_returns_correct_structure(self):
        """Test that calculate_pagination returns all required fields."""
        result = calculate_pagination(total_items=100, page=1, per_page=10)

        assert "page" in result
        assert "per_page" in result
        assert "total_items" in result
        assert "total_pages" in result
        assert "has_prev" in result
        assert "has_next" in result

    def test_calculate_pagination_first_page(self):
        """Test pagination for first page."""
        result = calculate_pagination(total_items=100, page=1, per_page=10)

        assert result["page"] == 1
        assert result["per_page"] == 10
        assert result["total_items"] == 100
        assert result["total_pages"] == 10
        assert result["has_prev"] is False
        assert result["has_next"] is True

    def test_calculate_pagination_middle_page(self):
        """Test pagination for middle page."""
        result = calculate_pagination(total_items=100, page=5, per_page=10)

        assert result["page"] == 5
        assert result["total_pages"] == 10
        assert result["has_prev"] is True
        assert result["has_next"] is True

    def test_calculate_pagination_last_page(self):
        """Test pagination for last page."""
        result = calculate_pagination(total_items=100, page=10, per_page=10)

        assert result["page"] == 10
        assert result["total_pages"] == 10
        assert result["has_prev"] is True
        assert result["has_next"] is False

    def test_calculate_pagination_with_partial_last_page(self):
        """Test pagination when last page is not full."""
        result = calculate_pagination(total_items=95, page=10, per_page=10)

        assert result["total_pages"] == 10
        assert result["has_prev"] is True
        assert result["has_next"] is False

    def test_calculate_pagination_with_zero_items(self):
        """Test pagination with empty dataset."""
        result = calculate_pagination(total_items=0, page=1, per_page=10)

        assert result["page"] == 1
        assert result["total_items"] == 0
        assert result["total_pages"] == 0
        assert result["has_prev"] is False
        assert result["has_next"] is False

    def test_calculate_pagination_with_one_item(self):
        """Test pagination with single item."""
        result = calculate_pagination(total_items=1, page=1, per_page=10)

        assert result["total_pages"] == 1
        assert result["has_prev"] is False
        assert result["has_next"] is False

    def test_calculate_pagination_exact_page_boundary(self):
        """Test pagination when items exactly fill pages."""
        result = calculate_pagination(total_items=50, page=1, per_page=10)

        assert result["total_pages"] == 5
        assert result["has_next"] is True

    def test_calculate_pagination_default_per_page(self):
        """Test pagination with default per_page value."""
        result = calculate_pagination(total_items=100, page=1)

        assert result["per_page"] == 50  # Default value
        assert result["total_pages"] == 2

    def test_calculate_pagination_page_out_of_range(self):
        """Test pagination when requesting page beyond total pages."""
        result = calculate_pagination(total_items=10, page=5, per_page=10)

        # Should still return valid structure
        assert result["page"] == 5
        assert result["total_pages"] == 1
        assert result["has_next"] is False
