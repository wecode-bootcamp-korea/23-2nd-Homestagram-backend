from django.http import response
import jwt

from django.test                    import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock                  import MagicMock, patch

from users.models      import User, Bookmark
from postings.models   import DesignType, Posting, Comment, Tag
from my_settings       import SECRET_KEY, ALGORITHM
from products.models   import Product

class PostingTest(TestCase):
    @classmethod
    def setUpTestData(self):
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

        Product.objects.create(
            id            = 1,
            product_name  = '의자',
            price         = 10000,
            thumbnail_url = '123.com'
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
            'file'      : image_file,
            'list'       : '{"tags" : [{"xx" : 101, "yy" : 201,"product_id" : 1}]}'
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
            'content'    : 'just moved!',
            'design_type': '거실',
            'file'      : '',
            'list'       : '{"tags" : [{"xx" : 101, "yy" : 201,"product_id" : 1}]}'
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
            'content'    : 'just moved!',
            'design_type1': '거실',
            'file'      : image_file,
            'list'       : '{"tags" : [{"xx" : 101, "yy" : 201,"product_id" : 1}]}'
        }

        mocked_s3_client.upload = MagicMock(return_value=MockedResponse())
        response                = client.post("/posting", body, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE' : 'DESIGN_TYPE_DOES_NOT_EXIST'} )

    @patch('postings.views.boto3.client')
    def test_posting_tag_invalid_keys(self, mocked_s3_client):
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
            'content'    : 'just moved!',
            'design_type': '거실',
            'file'      : image_file,
            'list'       : '{"tags" : [{"xx_key_error" : 101, "yy" : 201,"product_id" : 1}]}'
        }

        mocked_s3_client.upload = MagicMock(return_value=MockedResponse())
        response                = client.post("/posting", body, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE' : 'KEY_ERROR'} )

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

class CommentTest(TestCase):
    @classmethod
    def setUpTestData(self):
        User.objects.create(
            id          = 1,
            nickname    = 'Jun',
            kakao_id    = 1,
            kakao_email = 'wecode@gmail.com'
        )

        self.access_token = jwt.encode({'id' : 1}, SECRET_KEY, algorithm=ALGORITHM)

        DesignType.objects.create(
            id   = 1,
            name = '거실'
        )

        Posting.objects.create(
            id          = 1,
            content     = 'World\'s Best Coding BootCamp WeCode',
            image_url   = '123.com',
            design_type = DesignType.objects.get(id=1),
            user        = User.objects.get(id=1)
        )

        Comment.objects.create(
            id      = 1,
            content = 'Wecode',
            posting = Posting.objects.get(id=1),
            user    = User.objects.get(id=1)
        )

    def tearDown(self):
        Posting.objects.all().delete()
        DesignType.objects.all().delete()
        User.objects.all().delete()

    def test_comment_post_success(self):
        client = Client()
        body = {
            'content' : 'Wecode'
        }
        response = client.post('/postings/1/comment', body, content_type='application/json', HTTP_AUTHORIZATION=self.access_token)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'MESSAGE' : 'COMMENT_CREATED'} )

    def test_comment_patch_success(self):
        client = Client()
        body = {
            'content' : 'Wecode1'
        }
        response = client.patch('/comment/1', body, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'MESSAGE' : 'COMMENT_EDITED'})

    def test_comment_delete_success(self):
        client = Client()
        response = client.delete('/comment/1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'MESSAGE' : 'COMMENT_DELETED'})

class PostingFeedTest(TestCase):
    @classmethod
    def setUpTestData(self):
        User.objects.create(
            id          = 1,
            nickname    = 'wecode',
            kakao_id    = 1,
            kakao_email = 'wecode@gmail.com'
        )

        DesignType.objects.create(
            id   = 1,
            name = '거실'
        )

        Posting.objects.create(
            id          = 1,
            content     = 'wow',
            image_url   = 'wecode_image1.com',
            design_type = DesignType.objects.get(id=1),
            user        = User.objects.get(id=1)
        )

        Comment.objects.create(
            id      = 1,
            content = 'hi',
            posting = Posting.objects.get(id=1),
            user    = User.objects.get(id=1)
        )

        Product.objects.create(
            id            = 1,
            product_name  = '의자',
            price         = 1000,
            thumbnail_url = 'wecode_image2.com'
        )

        Tag.objects.create(
            id         = 1,
            coordinate = '(101, 201)',
            posting    = Posting.objects.get(id=1),
            product    = Product.objects.get(id=1)
        )

        self.token    = jwt.encode({'id': 1}, SECRET_KEY, algorithm=ALGORITHM)

    def tearDown(self):
        Tag.objects.all().delete()
        Product.objects.all().delete()
        Comment.objects.all().delete()
        Posting.objects.all().delete()
        DesignType.objects.all().delete()
        User.objects.all().delete()

    def test_posting_public_feed_get_success(self):
        client   = Client()
        response = client.get('/postings/feed/public')

        self.assertEqual(response.status_code, 200)

    def test_posting_private_feed_get_success(self):
        client   = Client()
        headers  = {'HTTP_Authorization' : self.token}
        response = client.get('/postings/feed/private?page=1', **headers)

        self.assertEqual(response.status_code, 200)
