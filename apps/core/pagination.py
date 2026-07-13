"""Custom pagination for consistent API responses."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """Standard pagination with 50 items per page."""

    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data) -> Response:
        """Return paginated response with metadata."""
        return Response({
            'success': True,
            'data': data,
            'error': None,
            'meta': {
                'pagination': {
                    'count': self.page.paginator.count,
                    'page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                    'total_pages': self.page.paginator.num_pages,
                },
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
        })
