from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import pagination, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from config import settings

from .permissions import IsAuthorizedStaffUser


class AdminApiPagination(pagination.PageNumberPagination):
    """Pagination class with page size query param support."""

    page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE")
    max_page_size = settings.REST_FRAMEWORK.get("MAX_PAGE_SIZE")
    page_size_query_param = "page_size"
    page_query_param = "page"


@extend_schema(tags=["public-api"])
class PublicApiView(APIView):
    permission_classes = [IsAuthenticated]
