from django.http  import JsonResponse
from django.views import View

from products.models import Product, ProductImage, ProductOption
from decorators      import query_debugger

class ProductDetailView(View):
    @query_debugger
    def get(self, request, product_id):
        if not Product.objects.filter(id=product_id).exists():
            return JsonResponse({'MESSAGE' : 'PRODUCT_DOES_NOT_EXIST'}, status=400)

        product = Product.objects.prefetch_related('productimage_set', 'productoption_set', 'productoption_set__color').get(id=product_id) 
        
        return JsonResponse({
            'product_title' : product.product_name,
            'product_price' : round(product.price),
            'url'           : product.thumbnail_url,
            'product_images': [
                image.image_url for image in product.productimage_set.all()
            ],
            'product_option' : [
                {
                    'color_name' :  product_option.color.name,
                    'product_stocks' : product_option.stock
                } for product_option in product.productoption_set.all()
            ]
        })