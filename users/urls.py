from users.models import PurchaseHistory
from django.urls import path

from users.views import SocialSignInView, NicknameView, FollowView, PurchaseHistoryView

urlpatterns = [
    path('/signin', SocialSignInView.as_view()),
    path('/<int:user_id>/nickname', NicknameView.as_view()),
    path('/follow', FollowView.as_view()),
    path('/purchase-history', PurchaseHistoryView.as_view())
]