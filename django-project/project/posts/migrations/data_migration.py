from django.db import migrations
from posts.factories import PostRandomFactory, CommentRandomFactory
import random
from django.conf import settings


def create_test_data(apps, schema_editor):
    if not settings.DEBUG:
        return

    posts = PostRandomFactory.create_batch(20)
    for post in posts:
        CommentRandomFactory.create_batch(random.randint(1, 5), post=post)


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0002"),
    ]

    operations = [
        migrations.RunPython(create_test_data),
    ]
