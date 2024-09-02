from constance import config
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.exceptions import DisallowedHost
from django.middleware.common import CommonMiddleware
from django.shortcuts import redirect
from graphql import GraphQLError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
import graphene_django.debug


class CustomCommonMiddleware(CommonMiddleware):
    def process_request(self, request):
        try:
            return super().process_request(request)
        except DisallowedHost:
            return redirect(config.BACKEND_DOMAIN)


class JWTAuthorizationMiddleware(object):
    def resolve(self, next, root, info, **args):
        context = info.context

        user = self.get_jwt_user(context)

        info.context.user = user

        return next(root, info, **args)

    def get_jwt_user(self, request):
        jwt_authenticator = JWTAuthentication()
        try:
            user, _ = jwt_authenticator.authenticate(request)
        except InvalidToken:
            user = AnonymousUser()
        except TypeError:
            user = AnonymousUser()
        return user


class RateLimitMiddleware(object):
    def resolve(self, next, root, info, **args):
        ip = info.context.META.get('REMOTE_ADDR')
        cache_key = f'rate_limit:{ip}'
        request_count = cache.get(cache_key, 0)

        rate_limit = 88
        timeout = 86400

        if request_count >= rate_limit:
            raise GraphQLError("Rate limit exceeded. Try again later.")

        cache.set(cache_key, request_count + 1, timeout=timeout)

        return next(root, info, **args)
