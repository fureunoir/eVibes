from constance import config
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import DisallowedHost
from django.middleware.common import CommonMiddleware
from django.shortcuts import redirect
from django.utils import translation
from django.utils.cache import patch_vary_headers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CustomCommonMiddleware(CommonMiddleware):
    def process_request(self, request):
        try:
            return super().process_request(request)
        except DisallowedHost:
            return redirect(f'https://api.{config.BASE_DOMAIN}')


class CustomLocaleCommonMiddleware(CommonMiddleware):
    def process_request(self, request):
        super().process_request(request)

        locale = request.headers.get('X-Locale')
        if not locale:
            locale = 'en-gb'

        translation.activate(locale)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = translation.get_language()

        patch_vary_headers(response, ("Accept-Language",))
        response.headers.setdefault("Content-Language", language)

        translation.deactivate()
        return super().process_response(request, response)


class GrapheneJWTAuthorizationMiddleware(object):
    def resolve(self, next, root, info, **args):
        context = info.context

        user = self.get_jwt_user(context)

        info.context.user = user

        return next(root, info, **args)

    @staticmethod
    def get_jwt_user(request):
        jwt_authenticator = JWTAuthentication()
        try:
            user, _ = jwt_authenticator.authenticate(request)
        except InvalidToken:
            user = AnonymousUser()
        except TypeError:
            user = AnonymousUser()
        return user


class GrapheneLocaleMiddleware(object):
    def resolve(self, next, root, info, **args):
        context = info.context
        headers = context.headers

        locale = headers.get('X-Locale')
        if not locale:
            locale = translation.get_language_from_request(context) or 'en-GB'

        translation.activate(locale)
        context.LANGUAGE_CODE = translation.get_language()

        try:
            return next(root, info, **args)
        finally:
            translation.deactivate()
