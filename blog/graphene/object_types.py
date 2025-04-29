import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from blog.models import Post, PostTag


class PostType(DjangoObjectType):
    tags = graphene.List(lambda: PostTagType)
    content = graphene.String()

    class Meta:
        model = Post
        fields = "__all__"
        interfaces = (relay.Node,)
        filter_fields = ["is_active"]

    def resolve_content(self, info):
        return self.content.html.replace("\n", "<br/>")


class PostTagType(DjangoObjectType):
    class Meta:
        model = PostTag
        fields = "__all__"
        interfaces = (relay.Node,)
        filter_fields = ["is_active"]
