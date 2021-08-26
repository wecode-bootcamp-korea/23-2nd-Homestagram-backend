from django.urls import path

from postings.views import PostingView, BookmarkView, CommentView

urlpatterns = [
    path('', PostingView.as_view()),
    path('/<int:posting_id>/bookmark', BookmarkView.as_view()),
    path('/list', BookmarkView.as_view()),
    path('/<int:posting_id>/comment', CommentView.as_view()),
    path('/<int:comment_id>', CommentView.as_view())
]