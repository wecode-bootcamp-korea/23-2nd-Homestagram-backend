from django.urls import path

from users.views import SocialSignInView

urlpatterns = [
    path('/signin', SocialSignInView.as_view()),
]