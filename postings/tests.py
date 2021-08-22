import jwt

from django.test                    import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock                  import MagicMock, patch

from users.models      import User, Bookmark
from postings.models   import DesignType, Posting
from my_settings       import SECRET_KEY, ALGORITHM

class PostingTest(TestCase):
    def setUp(self):
        User.objects.create(
            id          = 1,
            nickname    = 'Jun',
            kakao_id    = 1,
            kakao_email = '123'
        )

        DesignType.objects.create(
            id   = 1,
            name = '거실'
        )

        Posting.objects.create(
            id          = 1,
            content     = '우리집',
            image_url   = '123',
            design_type = DesignType.objects.get(name='거실'),
            user        = User.objects.get(id=1)
        )
    
    def tearDown(self):
        Posting.objects.all().delete()
        DesignType.objects.all().delete()
        User.objects.all().delete()

    @patch('postings.views.boto3.client')
    def test_posting_success(self, mocked_s3_client):
        client = Client()
        access_token = jwt.encode({'id' : 1}, SECRET_KEY, algorithm=ALGORITHM)

        class MockedResponse:
            def upload(self):
                return None

        image_file = SimpleUploadedFile(
            'file.jpg',
            b'file_content',
            content_type='image/ief'
        )

        headers = {'HTTP_AUTHORIZATION': access_token}

        body = {
            'content'    : 'just moved!',
            'design_type': '거실',
            'image'      : image_file
        }

        mocked_s3_client.upload = MagicMock(return_value=MockedResponse())
        response                = client.post("/posting", body, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'MESSAGE' : 'POSTING_SUCCESS'} )

    @patch('postings.views.boto3.client')
    def test_posting_empty_image(self, mocked_s3_client):
        client       = Client()
        access_token = jwt.encode({'id' : 1}, SECRET_KEY, algorithm=ALGORITHM)

        class MockedResponse:
            def upload(self):
                return None

        headers = {'HTTP_AUTHORIZATION': access_token}

        body = {
            'content'     : 'just moved!',
            'design_type': '거실',
            'image'       : ''
        }

        mocked_s3_client.upload = MagicMock(return_value=MockedResponse())
        response                = client.post("/posting", body, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE' : 'IMAGE_EMPTY'} )

    @patch('postings.views.boto3.client')
    def test_posting_design_type_does_not_exist(self, mocked_s3_client):
        client       = Client()
        access_token = jwt.encode({'id' : 1}, SECRET_KEY, algorithm=ALGORITHM)

        class MockedResponse:
            def upload(self):
                return None

        headers = {'HTTP_AUTHORIZATION': access_token}

        image_file = SimpleUploadedFile(
            'file.jpg',
            b'file_content',
            content_type='image/ief'
        )

        body = {
            'content'     : 'just moved!',
            'design_type1': '거실',
            'image'       : image_file
        }

        mocked_s3_client.upload = MagicMock(return_value=MockedResponse())
        response                = client.post("/posting", body, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE' : 'DESIGN_TYPE_DOES_NOT_EXIST'} )

class BookmarkTest(TestCase):
    @classmethod
    def setUpTestData(self):
        DesignType.objects.create(
            id   = 1,
            name = '거실'
        )

        User.objects.create(
            id          = 1,
            nickname    = 'Jun',
            kakao_id    = 1,
            kakao_email = 'wecode@gmail.com'
        )

        Posting.objects.create(
            id          = 1,
            content     = '안녕',
            image_url   = 'https://homestagram.s3.ap-northeast-2.amazonaws.com/1.jpg',
            design_type = DesignType.objects.get(id=1),
            user        = User.objects.get(id=1)
        )

        Bookmark.objects.create(
            posting = Posting.objects.get(id=1),
            user    = User.objects.get(id=1)
        )

        self.token    = jwt.encode({'id': User.objects.get(id=1).id}, SECRET_KEY, algorithm=ALGORITHM)

    def tearDown(self):
        Bookmark.objects.all().delete()
        Posting.objects.all().delete()
        DesignType.objects.all().delete()
        User.objects.all().delete()

    def test_bookmark_create_success(self):
        Bookmark.objects.all().delete()

        client   = Client()
        header   = {'HTTP_Authorization' : self.token}
        response = client.post('/postings/1/bookmark', **header, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'MESSAGE' : 'BOOKMARK_CREATED'} )

    def test_bookmark_delete_success(self):
        client   = Client()
        header   = {'HTTP_Authorization' : self.token}
        response = client.post('/postings/1/bookmark', **header, content_type='application/json')

        self.assertEqual(response.status_code, 204)

    def test_bookmark_list_get_success(self):
        client = Client()
        response = client.get('/user/1/bookmarks', content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            { 'LIST' :
                [{
                    'posting_id'       : 1,
                    'posting_username' : 'Jun',
                    'posting_image_url': 'https://homestagram.s3.ap-northeast-2.amazonaws.com/1.jpg'
                }]
            }
        )