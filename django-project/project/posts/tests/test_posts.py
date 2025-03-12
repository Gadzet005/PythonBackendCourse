from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from users.factories import UserFactory
from posts.factories import PostFactory, CommentFactory
from posts.models import Post, PostLike
from posts.serializers import PostSerializer


class PostsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.client = APIClient()
        cls.auth_client = APIClient()
        cls.auth_client.force_authenticate(user=cls.user)

    def test_get_list_with_authenticated_user(self):
        my_public_post: Post = PostFactory.create(author=self.user)
        my_private_post: Post = PostFactory.create(author=self.user, is_published=False)
        public_post: Post = PostFactory.create()
        private_post: Post = PostFactory.create(is_published=False)

        response = self.auth_client.get("/api/posts/")
        posts = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(posts), 3)
        self.assertIn(PostSerializer(my_public_post).data, posts)
        self.assertIn(PostSerializer(my_private_post).data, posts)
        self.assertIn(PostSerializer(public_post).data, posts)
        self.assertNotIn(PostSerializer(private_post).data, posts)

    def test_get_list_with_anonymous_user(self):
        public_post: Post = PostFactory.create()
        private_post: Post = PostFactory.create(is_published=False)

        response = self.auth_client.get("/api/posts/")
        posts = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(posts), 1)
        self.assertIn(PostSerializer(public_post).data, posts)
        self.assertNotIn(PostSerializer(private_post).data, posts)

    def test_list_order(self):
        PostFactory.create_batch(
            5,
        )

        response = self.auth_client.get("/api/posts/")
        posts = response.json()
        post_likes = list(map(lambda post: int(post["likes"]), posts))

        self.assertEqual(sorted(post_likes, reverse=True), post_likes)

    def test_create_with_authenticated_user(self):
        response = self.auth_client.post(
            "/api/posts/", {"title": "Test Post", "content": "Test Content"}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        created_post = Post.objects.first()
        self.assertEqual(created_post.author, self.user)
        self.assertEqual(created_post.title, "Test Post")
        self.assertEqual(created_post.content, "Test Content")

    def test_create_with_anonymous_user(self):
        response = self.client.post(
            "/api/posts/", {"title": "Test Post", "content": "Test Content"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Post.objects.count(), 0)

    def test_get_public_post(self):
        post: Post = PostFactory.create(
            title="Test Title",
        )
        response = self.client.get(f"/api/posts/{post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "Test Title")

    def test_get_private_post_with_author(self):
        post: Post = PostFactory.create(
            title="Test Title", is_published=False, author=self.user
        )
        response = self.auth_client.get(f"/api/posts/{post.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "Test Title")

    def test_get_private_post_with_non_author(self):
        post: Post = PostFactory.create(title="Test Title", is_published=False)
        response = self.auth_client.get(f"/api/posts/{post.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_private_post_with_anonymous(self):
        post: Post = PostFactory.create(title="Test Title", is_published=False)
        response = self.client.get(f"/api/posts/{post.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_non_existing_post(self):
        response = self.client.get("/api/posts/1000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_with_author(self):
        post: Post = PostFactory.create(author=self.user, title="Test Title")
        response = self.auth_client.patch(
            f"/api/posts/{post.id}/", {"title": "Updated Title"}
        )
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.title, "Updated Title")

    def test_update_with_non_author(self):
        post: Post = PostFactory.create(
            title="Test Title",
        )
        response = self.auth_client.patch(
            f"/api/posts/{post.id}/", {"title": "Updated Title"}
        )
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(post.title, "Updated Title")

    def test_update_with_anonymous_user(self):
        post: Post = PostFactory.create(
            title="Test Title",
        )
        response = self.client.patch(
            f"/api/posts/{post.id}/", {"title": "Updated Title"}
        )
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(post.title, "Updated Title")

    def test_update_non_existing_post(self):
        response = self.client.patch("/api/posts/1000/", {"title": "Updated Title"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_with_author(self):
        post: Post = PostFactory.create(author=self.user)
        response = self.auth_client.delete(f"/api/posts/{post.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_with_non_author(self):
        post: Post = PostFactory.create()
        response = self.auth_client.delete(f"/api/posts/{post.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)

    def test_delete_with_anonymous_user(self):
        post: Post = PostFactory.create()
        response = self.client.delete(f"/api/posts/{post.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Post.objects.count(), 1)

    def test_delete_non_existing_post(self):
        response = self.client.delete("/api/posts/1000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_with_authenticated_user(self):
        post: Post = PostFactory.create()
        response = self.auth_client.post(f"/api/posts/{post.id}/like/")
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PostLike.objects.exists())
        self.assertEqual(post.likes, 1)

    def test_like_with_anonymous_user(self):
        post: Post = PostFactory.create()
        response = self.client.post(f"/api/posts/{post.id}/like/")
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(PostLike.objects.exists())
        self.assertEqual(post.likes, 0)

    def test_unlike_with_authenticated_user(self):
        post: Post = PostFactory.create()
        PostLike.objects.create(post=post, user=self.user)
        response = self.auth_client.delete(f"/api/posts/{post.id}/like/")
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PostLike.objects.exists())
        self.assertEqual(post.likes, 0)

    def test_unlike_with_anonymous_user(self):
        post: Post = PostFactory.create()
        PostLike.objects.create(user=self.user, post=post)
        response = self.client.delete(f"/api/posts/{post.id}/like/")
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(PostLike.objects.exists())
        self.assertEqual(post.likes, 1)

    def test_double_likes(self):
        post = PostFactory.create()
        self.auth_client.post(f"/api/posts/{post.id}/like/")
        response = self.auth_client.post(f"/api/posts/{post.id}/like/")
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(PostLike.objects.exists())
        self.assertEqual(post.likes, 1)

    def test_double_unlikes(self):
        post: Post = PostFactory.create()
        PostLike.objects.create(post=post, user=self.user)
        self.auth_client.delete(f"/api/posts/{post.id}/like/")
        response = self.auth_client.delete(f"/api/posts/{post.id}/like/")
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(PostLike.objects.exists())
        self.assertEqual(post.likes, 0)

    def test_like_not_found(self):
        response = self.auth_client.post("/api/posts/9999/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(PostLike.objects.exists())

    def test_unlike_not_found(self):
        response = self.auth_client.delete("/api/posts/9999/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_private_post(self):
        post: Post = PostFactory.create(is_published=False)
        response = self.auth_client.post(f"/api/posts/{post.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(PostLike.objects.exists())

    def test_unlike_private_post(self):
        post: Post = PostFactory.create(is_published=False)
        response = self.auth_client.delete(f"/api/posts/{post.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_posts_statistics(self):
        PostFactory.create(author=self.user)
        PostFactory.create(author=self.user)
        PostFactory.create()
        PostFactory.create(is_published=False)

        response = self.client.get("/api/posts/statistics/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"posts": 3, "unique_post_authors": 2})

    def test_public_post_statistics(self):
        post: Post = PostFactory.create(is_published=True, likes=55)
        CommentFactory.create(post=post)
        CommentFactory.create(post=post)

        response = self.client.get(f"/api/posts/{post.id}/statistics/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"likes": 55, "comments": 2})

    def test_private_post_statistics_with_author(self):
        post: Post = PostFactory.create(is_published=False, author=self.user, likes=55)
        CommentFactory.create(post=post)
        CommentFactory.create(post=post)

        response = self.auth_client.get(f"/api/posts/{post.id}/statistics/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"likes": 55, "comments": 2})

    def test_private_post_statistics_with_non_author(self):
        post: Post = PostFactory.create(is_published=False, author=self.user)
        CommentFactory.create(post=post)

        response = self.client.get(f"/api/posts/{post.id}/statistics/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_private_post_statistics_with_anonymous(self):
        post: Post = PostFactory.create(is_published=False)

        response = self.client.get(f"/api/posts/{post.id}/statistics/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
