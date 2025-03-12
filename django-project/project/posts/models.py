from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth.models import User

from posts.managers import PostManager, CommentManager


class Post(models.Model):
    title = models.CharField(max_length=50, db_index=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    is_published = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)

    objects: PostManager = PostManager()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: CommentManager = CommentManager()


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["post", "user"], name="unique_user_post_like")
        ]


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["comment", "user"], name="unique_user_comment_like"
            )
        ]
