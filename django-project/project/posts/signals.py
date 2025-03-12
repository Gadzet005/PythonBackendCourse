from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PostLike, CommentLike


@receiver(post_save, sender=PostLike)
def increment_likes_count(sender, instance, created, **kwargs):
    if created:
        instance.post.likes += 1
        instance.post.save()


@receiver(post_delete, sender=PostLike)
def decrement_likes_count(sender, instance, **kwargs):
    instance.post.likes -= 1
    instance.post.save()


@receiver(post_save, sender=CommentLike)
def increment_comment_likes_count(sender, instance, created, **kwargs):
    if created:
        instance.comment.likes += 1
        instance.comment.save()


@receiver(post_delete, sender=CommentLike)
def decrement_comment_likes_count(sender, instance, **kwargs):
    instance.comment.likes -= 1
    instance.comment.save()
