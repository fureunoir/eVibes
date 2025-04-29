import mimetypes
import os

import requests
from django.contrib.sitemaps.views import index as _sitemap_index_view
from django.contrib.sitemaps.views import sitemap as _sitemap_detail_view
from django.core.cache import cache
from django.core.exceptions import BadRequest
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django_ratelimit.decorators import ratelimit
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from djangorestframework_camel_case.util import camelize
from drf_spectacular.utils import extend_schema_view
from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView
from graphene_django.views import GraphQLView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import MultiPartRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_xml.renderers import XMLRenderer
from rest_framework_yaml.renderers import YAMLRenderer
from sentry_sdk import capture_exception

from core.docs.drf.views import (
    CACHE_SCHEMA,
    CONTACT_US_SCHEMA,
    LANGUAGE_SCHEMA,
    PARAMETERS_SCHEMA,
    REQUEST_CURSED_URL_SCHEMA,
    SEARCH_SCHEMA,
)
from core.elasticsearch import process_query
from core.models import DigitalAssetDownload
from core.serializers import (
    CacheOperatorSerializer,
    ContactUsSerializer,
    LanguageSerializer,
)
from core.utils import get_project_parameters, is_url_safe
from core.utils.caching import web_cache
from core.utils.emailing import contact_us_email
from core.utils.languages import get_flag_by_language
from evibes import settings
from evibes.settings import LANGUAGES


def sitemap_index(request, *args, **kwargs):
    response = _sitemap_index_view(request, *args, **kwargs)
    response['Content-Type'] = 'application/xml; charset=utf-8'
    return response


def sitemap_detail(request, *args, **kwargs):
    response = _sitemap_detail_view(request, *args, **kwargs)
    response['Content-Type'] = 'application/xml; charset=utf-8'
    return response


class CustomGraphQLView(GraphQLView):
    def get_context(self, request):
        return request


class CustomSwaggerView(SpectacularSwaggerView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["script_url"] = self.request.build_absolute_uri()
        return context


class CustomRedocView(SpectacularRedocView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["script_url"] = self.request.build_absolute_uri()
        return context


@extend_schema_view(**LANGUAGE_SCHEMA)
class SupportedLanguagesView(APIView):
    serializer_class = LanguageSerializer
    permission_classes = [
        AllowAny,
    ]
    renderer_classes = [CamelCaseJSONRenderer, MultiPartRenderer, XMLRenderer, YAMLRenderer]

    def get(self, request):
        return Response(
            data=self.serializer_class(
                [
                    {
                        "code": lang[0],
                        "name": lang[1],
                        "flag": get_flag_by_language(lang[0]),
                    }
                    for lang in LANGUAGES
                ],
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )


@extend_schema_view(**PARAMETERS_SCHEMA)
class WebsiteParametersView(APIView):
    serializer_class = None
    permission_classes = [
        AllowAny,
    ]
    renderer_classes = [CamelCaseJSONRenderer, MultiPartRenderer, XMLRenderer, YAMLRenderer]

    def get(self, request):
        return Response(data=camelize(get_project_parameters()), status=status.HTTP_200_OK)


@extend_schema_view(**CACHE_SCHEMA)
class CacheOperatorView(APIView):
    serializer_class = CacheOperatorSerializer
    permission_classes = [
        AllowAny,
    ]
    renderer_classes = [CamelCaseJSONRenderer, MultiPartRenderer, XMLRenderer, YAMLRenderer]

    def post(self, request, *args, **kwargs):
        return Response(
            data=web_cache(
                request,
                request.data.get("key"),
                request.data.get("data"),
                request.data.get("timeout"),
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema_view(**CONTACT_US_SCHEMA)
class ContactUsView(APIView):
    serializer_class = ContactUsSerializer
    renderer_classes = [CamelCaseJSONRenderer, MultiPartRenderer, XMLRenderer, YAMLRenderer]

    @ratelimit(key="ip", rate="2/h")
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_us_email.delay(serializer.validated_data)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(**REQUEST_CURSED_URL_SCHEMA)
class RequestCursedURLView(APIView):
    permission_classes = [
        AllowAny,
    ]
    renderer_classes = [CamelCaseJSONRenderer, MultiPartRenderer, XMLRenderer, YAMLRenderer]

    @ratelimit(key="ip", rate="10/h")
    def post(self, request, *args, **kwargs):
        url = request.data.get("url")
        if not is_url_safe(url):
            return Response(
                data={"error": _("only URLs starting with http(s):// are allowed")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            data = cache.get(url, None)
            if not data:
                response = requests.get(url, headers={"content-type": "application/json"})
                response.raise_for_status()
                data = camelize(response.json())
                cache.set(url, data, 86400)
            return Response(
                data=data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                data={"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema_view(**SEARCH_SCHEMA)
class GlobalSearchView(APIView):
    """
    A global search endpoint.
    It returns a response grouping matched items by index.
    """
    renderer_classes = [CamelCaseJSONRenderer, MultiPartRenderer, XMLRenderer, YAMLRenderer]

    def get(self, request, *args, **kwargs):
        return Response(camelize({"results": process_query(request.GET.get("q", "").strip())}))


def download_digital_asset_view(request, *args, **kwargs):
    try:
        uuid = force_str(urlsafe_base64_decode(kwargs["encoded_uuid"]))
        download = DigitalAssetDownload.objects.get(order_product__uuid=uuid)

        if download.num_downloads >= 1:
            raise BadRequest(_("you can only download the digital asset once"))

        download.num_downloads += 1
        download.save()

        file_path = download.order_product.product.stocks.first().digital_asset.file.path

        content_type, encoding = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/octet-stream"

        with open(file_path, "rb") as file:
            response = FileResponse(file, content_type=content_type)
            filename = os.path.basename(file_path)
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

    except BadRequest as e:
        return JsonResponse({"error": str(e)}, status=400)

    except DigitalAssetDownload.DoesNotExist:
        return JsonResponse({"error": "Digital asset not found"}, status=404)

    except Exception as e:
        capture_exception(e)
        return JsonResponse({"error": "An error occurred while trying to download the digital asset"}, status=500)


def favicon_view(request, *args, **kwargs):
    try:
        favicon_path = os.path.join(settings.BASE_DIR, "static/favicon.png")
        return FileResponse(open(favicon_path, "rb"), content_type="image/x-icon")
    except FileNotFoundError:
        raise Http404(_("favicon not found"))


def index(request, *args, **kwargs):
    return redirect("admin:index")
