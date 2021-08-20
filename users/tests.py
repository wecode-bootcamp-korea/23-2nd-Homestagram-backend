from unittest.mock import patch, MagicMock

from django.test import TestCase, Client

from users.models import User

class SignUpTest(TestCase):
    def setUp(self):
        User.objects.create(
            id          = 1,
            nickname    = "test",
            kakao_id    = 1111111111,
            kakao_email = "test@test.com",
        )

    def tearDown(self):
        User.objects.all().delete()

    @patch("users.views.requests")
    def test_signup_new_user_success(self, mocked_requests):
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

        data = {
            'access_token' : 'fake_access_token',
            'nickname'     : 'test2' 
        }

        response = client.post('/users/signup', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 201)

    @patch("users.views.requests")
    def test_signup_invalid_kakao_token(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "msg": "this access token does not exist",
                    "code": -401
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())

        data = {
            'access_token' : 'fake_access_token',
            'nickname'     : 'test2' 
        }

        response = client.post('/users/signup', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE':'INVALID_KAKAO_TOKEN'})

    @patch("users.views.requests")
    def test_signup_need_email_agreement(self, mocked_requests):
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
                        'email_needs_agreement': True,
                        'is_email_valid': True,
                        'is_email_verified': True,
                    }
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())

        data = {
            'access_token' : 'fake_access_token',
            'nickname'     : 'test2' 
        }

        response = client.post('/users/signup', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE':'NEED_EMAIL_AGREEMENT'})

    @patch("users.views.requests")
    def test_signup_nickname_already_exist(self, mocked_requests):
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

        data = {
            'access_token' : 'fake_access_token',
            'nickname'     : 'test' 
        }

        response = client.post('/users/signup', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {'MESSAGE':'NICKNAME_ALREADY_EXISTS'})

    @patch("users.views.requests")
    def test_signup_token_key_error(self, mocked_requests):
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

        data = {
            'access_token22222' : 'fake_access_token',
            'nickname'          : 'test' 
        }

        response = client.post('/users/signup', content_type='application/json', data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE':'KEY_ERROR'})