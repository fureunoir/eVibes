from drf_spectacular.utils import inline_serializer
from rest_framework import status
from rest_framework.fields import CharField

error = inline_serializer("error", fields={"detail": CharField()})

BASE_ERRORS = {
    status.HTTP_400_BAD_REQUEST: error,
    status.HTTP_401_UNAUTHORIZED: error,
    status.HTTP_403_FORBIDDEN: error,
    status.HTTP_404_NOT_FOUND: error,
    status.HTTP_405_METHOD_NOT_ALLOWED: error,
    status.HTTP_500_INTERNAL_SERVER_ERROR: error,
}
