from django.conf import settings
from rest_framework import pagination


class PageSizeParamPagination(pagination.PageNumberPagination):
    """Pagination class with page size query param support."""

    page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE")
    max_page_size = settings.REST_FRAMEWORK.get("MAX_PAGE_SIZE")
    page_size_query_param = "page_size"
    page_query_param = "page"
