import logging
import traceback
from os import getenv

from constance import config
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import DisallowedHost
from django.http import HttpResponseForbidden
from django.middleware.common import CommonMiddleware
from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from sentry_sdk import capture_exception

logger = logging.getLogger(__name__)


class CustomCommonMiddleware(CommonMiddleware):
    def process_request(self, request):
        try:
            return super().process_request(request)
        except DisallowedHost:
            return redirect(f"https://api.{config.BASE_DOMAIN}")


class GrapheneJWTAuthorizationMiddleware:
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


class BlockInvalidHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_hosts = getenv("ALLOWED_HOSTS").split(" ")
        if request.META.get("HTTP_HOST") not in allowed_hosts and "*" not in allowed_hosts:
            return HttpResponseForbidden("Invalid Host Header")
        return self.get_response(request)


class GrapheneLoggingErrorsDebugMiddleware:
    def resolve(self, next, root, info, **args):
        try:
            return next(root, info, **args)
        except Exception as e:
            logger.error("Error occurred in GraphQL execution:", exc_info=True)
            if bool(int(getenv("DEBUG"))):
                logger.error(traceback.format_exc())
            capture_exception(e)
            raise e
