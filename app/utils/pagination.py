"""
Pagination helper utilities.

Provides functions to calculate pagination metadata for API responses.
"""

import math
from typing import Dict, Union


def calculate_pagination(
    total_items: int, page: int, per_page: int = 50
) -> Dict[str, Union[int, bool]]:
    """
    Calculate pagination metadata.

    Args:
        total_items (int): Total number of items in dataset
        page (int): Current page number (1-indexed)
        per_page (int): Items per page (default: 50)

    Returns:
        dict: Pagination metadata with keys:
            - page (int): Current page number
            - per_page (int): Items per page
            - total_items (int): Total items in dataset
            - total_pages (int): Total number of pages
            - has_prev (bool): True if there's a previous page
            - has_next (bool): True if there's a next page
    """
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 0

    return {
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }
