from django.urls import path

import posts.views as views


urlpatterns = [
    path("", views.PostListView.as_view(), name="post-list"),
    path("<int:pk>/", views.PostView.as_view(), name="post"),
    path("my/", views.UserPostListView.as_view(), name="user-post-list"),
    path(
        "<int:post_pk>/comments/",
        views.CommentListView.as_view(),
        name="comment-list",
    ),
    path(
        "comments/<int:pk>/",
        views.CommentView.as_view(),
        name="comment",
    ),
    path(
        "statistics/",
        views.PostListStatisticsView.as_view(),
        name="post-list-statistics",
    ),
    path(
        "<int:post_pk>/statistics/",
        views.PostStatisticsView.as_view(),
        name="post-statistics",
    ),
    path(
        "<int:post_pk>/like/",
        views.PostLikeView.as_view(),
        name="post-like",
    ),
    path(
        "comments/<int:comment_pk>/like/",
        views.CommentLikeView.as_view(),
        name="comment-like",
    ),
]
