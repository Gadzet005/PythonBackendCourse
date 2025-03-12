from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from users.factories import UserFactory
from posts.factories import CommentFactory, PostFactory
from posts.models import Comment, CommentLike, Post
from posts.serializers import CommentSerializer


class CommentsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.client = APIClient()
        cls.auth_client = APIClient()
        cls.auth_client.force_authenticate(user=cls.user)

    def test_get_list(self):
        post = PostFactory()
        comment1 = CommentFactory.create(post=post, author=self.user)
        comment2 = CommentFactory.create(post=post)

        response = self.client.get(f"/api/posts/{post.id}/comments/")
        comments = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(comments), 2)
        self.assertIn(CommentSerializer(comment1).data, comments)
        self.assertIn(CommentSerializer(comment2).data, comments)

    def test_get_list_for_non_existing_post(self):
        response = self.client.get("/api/posts/1000/comments/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_order(self):
        post: Post = PostFactory.create()
        CommentFactory.create_batch(5, post=post)

        response = self.client.get(f"/api/posts/{post.id}/comments/")
        comments = response.json()
        comment_likes = list(map(lambda comment: comment["likes"], comments))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(comment_likes, reverse=True), comment_likes)

    def test_create_with_authorized_user(self):
        post = PostFactory()
        response = self.auth_client.post(
            f"/api/posts/{post.id}/comments/", {"content": "Test Comment"}
        )
        created_comment = Comment.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(created_comment.author, self.user)
        self.assertEqual(created_comment.content, "Test Comment")
        self.assertEqual(created_comment.post, post)

    def test_create_with_anonymous_user(self):
        post = PostFactory()
        response = self.client.post(
            f"/api/posts/{post.id}/comments/", {"content": "Test Comment"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Comment.objects.count(), 0)

    def test_create_for_not_existing_post(self):
        response = self.auth_client.post(
            "/api/posts/1000/comments/", {"content": "Test Comment"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comment(self):
        comment: Comment = CommentFactory.create()
        response = self.client.get(f"/api/posts/comments/{comment.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), CommentSerializer(comment).data)

    def test_get_not_existing_comment(self):
        response = self.client.get("/api/posts/comments/1000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_comment_with_author(self):
        comment: Comment = CommentFactory.create(
            author=self.user, content="Test Comment"
        )
        response = self.auth_client.patch(
            f"/api/posts/comments/{comment.id}/", {"content": "Updated Comment"}
        )
        comment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.content, "Updated Comment")

    def test_update_comment_with_non_author(self):
        comment: Comment = CommentFactory.create(content="Test Comment")
        response = self.auth_client.patch(
            f"/api/posts/comments/{comment.id}/", {"content": "Updated Comment"}
        )
        comment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(comment.content, "Test Comment")

    def test_update_comment_with_anonymous_user(self):
        comment: Comment = CommentFactory.create(content="Test Comment")
        response = self.client.patch(
            f"/api/posts/comments/{comment.id}/", {"content": "Updated Comment"}
        )
        comment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(comment.content, "Test Comment")

    def test_update_comment_for_not_existing_comment(self):
        response = self.auth_client.patch(
            "/api/posts/comments/1000/", {"content": "Updated Comment"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_comment_with_author(self):
        comment: Comment = CommentFactory.create(author=self.user)
        response = self.auth_client.delete(f"/api/posts/comments/{comment.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_with_non_author(self):
        comment: Comment = CommentFactory.create()
        response = self.auth_client.delete(f"/api/posts/comments/{comment.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 1)

    def test_delete_comment_with_anonymous_user(self):
        comment: Comment = CommentFactory.create()
        response = self.client.delete(f"/api/posts/comments/{comment.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_delete_comment_for_not_existing_comment(self):
        response = self.auth_client.delete("/api/posts/comments/1000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_comment_with_authenticated_user(self):
        comment: Comment = CommentFactory.create()
        response = self.auth_client.post(f"/api/posts/comments/{comment.id}/like/")
        comment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CommentLike.objects.count(), 1)
        self.assertEqual(comment.likes, 1)

    def test_like_comment_with_anonymous_user(self):
        comment: Comment = CommentFactory.create()
        response = self.client.post(f"/api/posts/comments/{comment.id}/like/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(CommentLike.objects.count(), 0)
        self.assertEqual(comment.likes, 0)

    def test_like_comment_for_not_existing_comment(self):
        response = self.auth_client.post("/api/posts/comments/1000/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unlike_comment_with_authenticated_user(self):
        comment: Comment = CommentFactory.create()
        CommentLike.objects.create(comment=comment, user=self.user)
        response = self.auth_client.delete(f"/api/posts/comments/{comment.id}/like/")
        comment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CommentLike.objects.count(), 0)
        self.assertEqual(comment.likes, 0)

    def test_unlike_comment_with_anonymous_user(self):
        comment: Comment = CommentFactory.create()
        CommentLike.objects.create(comment=comment, user=self.user)
        response = self.client.delete(f"/api/posts/comments/{comment.id}/like/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(CommentLike.objects.count(), 1)
        self.assertEqual(comment.likes, 1)

    def test_unlike_comment_for_not_existing_comment(self):
        response = self.auth_client.delete("/api/posts/comments/1000/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_double_like(self):
        comment: Comment = CommentFactory.create()
        CommentLike.objects.create(comment=comment, user=self.user)
        self.auth_client.post(f"/api/posts/comments/{comment.id}/like/")
        response = self.auth_client.post(f"/api/posts/comments/{comment.id}/like/")
        comment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CommentLike.objects.count(), 1)
        self.assertEqual(comment.likes, 1)

    def test_double_unlike(self):
        comment: Comment = CommentFactory.create()
        CommentLike.objects.create(comment=comment, user=self.user)
        self.auth_client.delete(f"/api/posts/comments/{comment.id}/like/")
        response = self.auth_client.delete(f"/api/posts/comments/{comment.id}/like/")
        comment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CommentLike.objects.count(), 0)
        self.assertEqual(comment.likes, 0)
