from django.urls import path

from postings.views import PostingView, BookmarkView

urlpatterns = [
    path('', PostingView.as_view()),
    path('/<int:posting_id>/bookmark', BookmarkView.as_view()),
    path('/<int:user_id>/bookmarks', BookmarkView.as_view())
]