from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from blog.models import Post, PostTag


class PostTagSerializer(ModelSerializer):
    class Meta:
        model = PostTag
        fields = "__all__"


class PostSerializer(ModelSerializer):
    tags = PostTagSerializer(many=True)
    content = SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"

    def get_content(self, obj: Post) -> str:
        return obj.content.html.replace("\n", "<br/>")
