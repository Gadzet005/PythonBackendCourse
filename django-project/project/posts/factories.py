import factory

from posts.models import Post, Comment
from users.factories import UserFactory


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker("sentence")
    content = factory.Faker("paragraph")
    author = factory.SubFactory(UserFactory)
    likes = 0
    is_published = True


class PostRandomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker("sentence")
    content = factory.Faker("paragraph")
    author = factory.SubFactory(UserFactory)
    likes = factory.Faker("random_int", min=0, max=100)
    is_published = factory.Faker("boolean")


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    content = factory.Faker("sentence")
    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    likes = 0


class CommentRandomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    content = factory.Faker("sentence")
    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    likes = factory.Faker("random_int", min=0, max=100)
