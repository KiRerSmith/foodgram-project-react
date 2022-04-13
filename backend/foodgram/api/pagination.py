from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size = settings.PAGE_LIMIT
    page_size_query_param = 'limit'
