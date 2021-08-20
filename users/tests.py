import json, jwt

from django.test import TestCase
from django.http import HttpRequest

from my_settings          import ALGORITHM 
from homestagram.settings import SECRET_KEY
from users.utils          import SignInDecorator
from users.models         import User

class SignInDecoratorTest(TestCase):
    def setUp(self):
        self.users = User.objects.bulk_create([
            User(
                id          = 1,
                nickname    = "test",
                kakao_id    = 1111111111,
                kakao_email = "test@test.com"
            ),
            User(
                id          = 2,
                kakao_id    = 1111111112,
                kakao_email = "test123@test.com"
            )
        ])

    def tearDown(self):
        User.objects.all().delete()
        
    
    def test_decorator_success(self):
        access_token = jwt.encode({'id': self.users[0].id}, SECRET_KEY, algorithm=ALGORITHM)
        
        fake_request         = HttpRequest()
        fake_request.headers = {'Authorization':access_token}

        @SignInDecorator
        def user_id(self, request):
            return f'user_id is {request.user.id}'
        
        self.assertEqual(user_id(fake_request),'user_id is 1')

    def test_decorator_existing_user_need_nickname(self):
        access_token = jwt.encode({'id': self.users[1].id}, SECRET_KEY, algorithm=ALGORITHM)
        
        fake_request         = HttpRequest()
        fake_request.headers = {'Authorization':access_token}

        @SignInDecorator
        def user_id(self, request):
            return f'user_id is {request.user.id}'

        self.assertEqual(json.loads(user_id(fake_request).content)['MESSAGE'],'NEED_NICKNAME')

    def test_decorator_no_token(self):
        fake_request = HttpRequest()

        @SignInDecorator
        def user_id(self, request):
            return f'user_id is {request.user.id}'

        self.assertEqual(json.loads(user_id(fake_request).content)['MESSAGE'],'NEED_LOGIN')

    def test_decorator_invalid_token(self):
        fake_request         = HttpRequest()
        fake_request.headers = {'Authorization':'foobar'}

        @SignInDecorator
        def user_id(self, request):
            return f'user_id is {request.user.id}'

        self.assertEqual(json.loads(user_id(fake_request).content)['MESSAGE'],'INVALID_TOKEN')

    
