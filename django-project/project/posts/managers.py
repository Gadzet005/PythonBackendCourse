from django.db import models
from django.db.models import Q


class PostQuerySet(models.QuerySet):
    def most_popular(self):
        return self.order_by("-likes")

    def posts_count(self):
        return self.count()

    def unique_post_authors_count(self):
        return self.values("author").distinct().count()


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def allowed_for_user(self, user=None):
        if user and user.is_authenticated:
            queryset = self.get_queryset().filter(Q(is_published=True) | Q(author=user))
        else:
            queryset = self.get_queryset().filter(is_published=True)
        return queryset

    def post_comments_count(self, post_id):
        return self.get_queryset().get(id=post_id).comment_set.count()


class CommentQuerySet(models.QuerySet):
    def most_popular(self):
        return self.order_by("-likes")


class CommentManager(models.Manager):
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)
