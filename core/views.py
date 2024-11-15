import os

from django.http import FileResponse, Http404
from django.shortcuts import redirect
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView
from graphene_django.views import GraphQLView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from evibes import settings
from evibes.settings import LANGUAGES


class CustomGraphQLView(GraphQLView):
    def get_context(self, request):
        # Return the request as context to access request.user in resolvers
        return request


class CustomSwaggerView(SpectacularSwaggerView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['script_url'] = self.request.build_absolute_uri()  # Set script_url if missing
        return context


class CustomRedocView(SpectacularRedocView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['script_url'] = self.request.build_absolute_uri()  # Set script_url if missing
        return context


class SupportedLanguagesView(APIView):
    serializer_class = None
    permission_classes = [AllowAny, ]
    authentication_classes = []

    def get(self, request):
        return Response(data=LANGUAGES, status=status.HTTP_200_OK)


def favicon_view(request, *args, **kwargs):
    """
    Serve the favicon.ico file.
    """
    try:
        # Construct the absolute path to the favicon.ico file
        favicon_path = os.path.join(settings.BASE_DIR, 'static/favicon.png')
        return FileResponse(open(favicon_path, 'rb'), content_type='image/x-icon')
    except FileNotFoundError:
        raise Http404("favicon.ico not found")


def index(request, *args, **kwargs):
    return redirect('admin:index')

def test_sentry(request, *args, **kwargs):
    raise ValueError('This is a test error')
