from rest_framework import serializers

from posts.models import Post, Comment, PostLike, CommentLike


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "author",
            "likes",
            "is_published",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "likes",
            "updated_at",
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "content",
            "likes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "post", "author", "likes", "created_at", "updated_at"]
