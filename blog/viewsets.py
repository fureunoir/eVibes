from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from blog.filters import PostFilter
from blog.models import Post
from blog.serializers import PostSerializer
from core.permissions import EvibesPermission


class PostViewSet(ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (EvibesPermission,)
    queryset = Post.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
