from django.test import TestCase, Client

from .models import Product, ProductImage, ProductOption, Color

class ProductDetailTest(TestCase):
    @classmethod
    def setUpTestData(self):
        Product.objects.create(
            id            = 1,
            product_name  = '의자1',
            price         = 1000,
            thumbnail_url = 'https://homestagram.s3.abc'
        )

        ProductImage.objects.create(
            id        = 1,
            image_url = 'https://homestagram.s3.abc',
            product   = Product.objects.get(id=1)
        )

        Color.objects.create(
            id   = 1,
            name = '검은색'
        )

        ProductOption.objects.create(
            id      = 1,
            stock   = 100,
            color   = Color.objects.get(id=1),
            product = Product.objects.get(id=1)
        )

    def tearDown(self):
        Product.objects.all().delete()
        ProductImage.objects.all().delete()
        Color.objects.all().delete()
        ProductOption.objects.all().delete()

    def test_product_detail_get_sucess(self):
        client = Client()

        response = client.get('/products/1/detail', content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'product_title' : '의자1',
                'product_price' : 1000,
                'url'           : 'https://homestagram.s3.abc',
                'product_images': [
                    'https://homestagram.s3.abc'
                ],
                "product_option": [{
                    "color_name"   : "검은색",
                    "product_stocks": 100
                }]
            }
        )
    
    def test_product_detail_invlid_product_id(self):
        client = Client()
        
        response = client.get('/products/80/detail', content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE' : 'PRODUCT_DOES_NOT_EXIST'})




