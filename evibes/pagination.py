from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"  # name of the query parameter, you can use any

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {"forward": self.get_next_link(), "backward": self.get_previous_link()},
                "counts": {
                    "total_pages": self.page.paginator.num_pages,
                    "page_size": self.page_size,
                    "total_items": self.page.paginator.count,
                },
                "data": data,
            }
        )

    def get_paginated_response_schema(self, data_schema):
        return {
            "type": "object",
            "properties": {
                "links": {
                    "type": "object",
                    "properties": {
                        "forward": {
                            "type": "string",
                            "nullable": True,
                            "format": "uri",
                            "description": "URL to the next page",
                        },
                        "backward": {
                            "type": "string",
                            "nullable": True,
                            "format": "uri",
                            "description": "URL to the previous page",
                        },
                    },
                },
                "total_pages": {
                    "type": "integer",
                    "example": 10,
                    "description": "Total number of pages",
                },
                "page_size": {
                    "type": "integer",
                    "example": 10,
                    "description": "Number of items per page",
                },
                "total_items": {
                    "type": "integer",
                    "example": 100,
                    "description": "Total number of items",
                },
                "data": data_schema,
            },
        }
