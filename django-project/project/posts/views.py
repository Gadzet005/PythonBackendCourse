from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

from posts.models import Comment, Post, PostLike, CommentLike
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import CommentSerializer, PostSerializer

POST_NOT_FOUND = NotFound("Post not found")
COMMENT_NOT_FOUND = NotFound("Comment not found")


class PostListView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Post.objects.allowed_for_user(self.request.user).most_popular()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        return Post.objects.allowed_for_user(self.request.user)


class UserPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author_id=self.request.user.id)


class CommentListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def ensure_post_exists(self):
        try:
            Post.objects.allowed_for_user(self.request.user).get(
                pk=self.kwargs["post_pk"]
            )
        except Post.DoesNotExist:
            raise POST_NOT_FOUND

    def list(self, request, post_pk):
        self.ensure_post_exists()
        return super().list(request, post_pk)

    def create(self, request, post_pk):
        self.ensure_post_exists()
        return super().create(request, post_pk)

    def get_queryset(self):
        return (
            Comment.objects.all().filter(post_id=self.kwargs["post_pk"]).most_popular()
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post_id=self.kwargs.get("post_pk"))


class CommentView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]


class PostListStatisticsView(APIView):
    def get(self, request):
        posts = Post.objects.allowed_for_user(request.user)
        posts_count = posts.posts_count()
        unique_post_authors_count = posts.unique_post_authors_count()
        return Response(
            {
                "posts": posts_count,
                "unique_post_authors": unique_post_authors_count,
            }
        )


class PostStatisticsView(APIView):
    def get(self, request, post_pk):
        post = Post.objects.allowed_for_user(request.user).filter(id=post_pk)
        if not post.exists():
            raise POST_NOT_FOUND

        comments_count = Post.objects.post_comments_count(post_pk)
        return Response(
            {
                "comments": comments_count,
                "likes": post[0].likes,
            }
        )


class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def ensure_post_exists(self):
        try:
            Post.objects.allowed_for_user(self.request.user).get(
                pk=self.kwargs["post_pk"]
            )
        except Post.DoesNotExist:
            raise POST_NOT_FOUND

    def post(self, request, post_pk):
        self.ensure_post_exists()

        _, created = PostLike.objects.get_or_create(post_id=post_pk, user=request.user)

        if not created:
            return Response(
                {"detail": "User already liked this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_200_OK)

    def delete(self, request, post_pk):
        self.ensure_post_exists()

        try:
            post_like = PostLike.objects.get(post_id=post_pk, user=request.user)
        except PostLike.DoesNotExist:
            return Response(
                {"detail": "User did not like this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post_like.delete()
        return Response(status=status.HTTP_200_OK)


class CommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def ensure_comment_exists(self):
        try:
            comment = Comment.objects.get(pk=self.kwargs["comment_pk"])
            Post.objects.allowed_for_user(self.request.user).get(pk=comment.post_id)
        except Post.DoesNotExist:
            raise POST_NOT_FOUND
        except Comment.DoesNotExist:
            raise COMMENT_NOT_FOUND

    def post(self, request, comment_pk):
        self.ensure_comment_exists()

        _, created = CommentLike.objects.get_or_create(
            comment_id=comment_pk, user=request.user
        )

        if not created:
            return Response(
                {"detail": "User already liked this comment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_200_OK)

    def delete(self, request, comment_pk):
        self.ensure_comment_exists()

        try:
            comment_like = CommentLike.objects.get(
                comment_id=comment_pk, user=request.user
            )
        except CommentLike.DoesNotExist:
            return Response(
                {"detail": "User did not like this comment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment_like.delete()
        return Response(status=status.HTTP_200_OK)
