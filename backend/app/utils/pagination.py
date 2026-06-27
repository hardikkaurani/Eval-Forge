from typing import Generic, TypeVar
from pydantic import BaseModel
from app.utils.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


class PageMetadata(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMetadata


def get_limit_offset(
    page: int | None = None, page_size: int | None = None
) -> tuple[int, int]:
    """Calculates limit and offset for SQL queries based on page parameters.

    Enforces minimum values and a maximum page size configuration.
    """
    p = page if (page is not None and page > 0) else DEFAULT_PAGE
    ps = page_size if (page_size is not None and page_size > 0) else DEFAULT_PAGE_SIZE

    if ps > MAX_PAGE_SIZE:
        ps = MAX_PAGE_SIZE

    limit = ps
    offset = (p - 1) * ps
    return limit, offset


def create_pagination_meta(
    page: int,
    page_size: int,
    total_items: int,
) -> PageMetadata:
    """Builds the PageMetadata schema helper."""
    total_pages = (
        (total_items + page_size - 1) // page_size if page_size > 0 else 0
    )
    return PageMetadata(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
