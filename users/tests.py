import json, jwt
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
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

class SignInTest(TestCase):
    def setUp(self):
        User.objects.bulk_create([
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

    @patch("users.views.requests")
    def test_signin_existing_user_success(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id": 1111111111,
                    'connected_at': '2021-08-19T07:59:52Z', 
                    'properties': {'nickname': 'testtest'}, 
                    'kakao_account': {
                        'profile_nickname_needs_agreement': False,
                        'profile': {'nickname': 'testtest'},
                        'has_email': True,
                        'email_needs_agreement': False,
                        'is_email_valid': True,
                        'is_email_verified': True,
                        'email': 'test@test.com'
                    }
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())

        data = {'access_token' : 'fake_access_token'}
        response = client.post('/users/signin', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['nickname'], 'test')

    @patch("users.views.requests")
    def test_signin_new_user_create_success(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id": 2222222222,
                    'connected_at': '2021-08-19T07:59:52Z', 
                    'properties': {'nickname': 'testtest'}, 
                    'kakao_account': {
                        'profile_nickname_needs_agreement': False,
                        'profile': {'nickname': 'testtest'},
                        'has_email': True,
                        'email_needs_agreement': False,
                        'is_email_valid': True,
                        'is_email_verified': True,
                        'email': 'test2@test.com'
                    }
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())

        data = {'access_token' : 'fake_access_token'}
        response = client.post('/users/signin', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['nickname'], None)

    @patch("users.views.requests")
    def test_signin_existing_user_need_nickname(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id": 1111111112,
                    'connected_at': '2021-08-19T07:59:52Z', 
                    'properties': {'nickname': 'testtest'}, 
                    'kakao_account': {
                        'profile_nickname_needs_agreement': False,
                        'profile': {'nickname': 'testtest'},
                        'has_email': True,
                        'email_needs_agreement': False,
                        'is_email_valid': True,
                        'is_email_verified': True,
                        'email': 'test123@test.com'
                    }
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())

        data = {'access_token' : 'fake_access_token'}
        response = client.post('/users/signin', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['nickname'], None)

    @patch("users.views.requests")
    def test_signin_token_key_error(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id": 2222222222,
                    'connected_at': '2021-08-19T07:59:52Z', 
                    'properties': {'nickname': 'testtest'}, 
                    'kakao_account': {
                        'profile_nickname_needs_agreement': False,
                        'profile': {'nickname': 'testtest'},
                        'has_email': True,
                        'email_needs_agreement': False,
                        'is_email_valid': True,
                        'is_email_verified': True,
                        'email': 'test@test.com'
                    }
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())

        data = {'access_token2222' : 'fake_access_token'}

        response = client.post('/users/signin', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE':'KEY_ERROR'})

class NicknameRegisterTest(TestCase):
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

    def test_nickname_new_register_success(self):
        client = Client()
        
        data = {'nickname': "test2"}
        response = client.post('/users/' + f'{self.users[1].id}' + '/nickname', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'MESSAGE':'UPDATED'})

    def test_nickname_update_success(self):
        client = Client()
        
        data = {'nickname': "test3"}
        response = client.post('/users/' + f'{self.users[0].id}' + '/nickname', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'MESSAGE':'UPDATED'})
        self.assertEqual(User.objects.get(id=self.users[0].id).nickname, 'test3')
    
    def test_nickname_register_already_exist(self):
        client = Client()
        
        data = {'nickname': "test"}
        response = client.post('/users/' + f'{self.users[1].id}' + '/nickname', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {'MESSAGE':'NICKNAME_ALREADY_EXISTS'})
