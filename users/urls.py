from django.urls import path

from users.views import SocialSignInView, NicknameView

urlpatterns = [
    path('/signin', SocialSignInView.as_view()),
    path('/<int:user_id>/nickname', NicknameView.as_view()),
]