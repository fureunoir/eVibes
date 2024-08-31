import os

from django.http import FileResponse, Http404
from graphene_django.views import GraphQLView

from evibes import settings


class CustomGraphQLView(GraphQLView):
    def get_context(self, request):
        # Return the request as context to access request.user in resolvers
        return request


def favicon_view(request):
    """
    Serve the favicon.ico file.
    """
    try:
        # Construct the absolute path to the favicon.ico file
        favicon_path = os.path.join(settings.BASE_DIR, 'static/favicon.ico')
        return FileResponse(open(favicon_path, 'rb'), content_type='image/x-icon')
    except FileNotFoundError:
        raise Http404("favicon.ico not found")
