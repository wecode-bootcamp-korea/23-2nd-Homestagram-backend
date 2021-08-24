import boto3, uuid, json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction
from django.db.models import Max

from postings.models          import Posting, DesignType, Tag
from homestagram.settings     import AWS_STORAGE_BUCKET_NAME, AWS_S3_SECRET_ACCESS_KEY, AWS_S3_ACCESS_KEY_ID, S3_URL
from users.utils              import SignInDecorator
from users.models             import Bookmark, User
from products.models          import Product

class PostingView(View):
    @SignInDecorator
    @transaction.atomic
    def post(self, request):
        try:
            content     = request.POST.get('content')
            design_type = request.POST.get('design_type')
            image       = request.FILES.get('file')
            tags        = json.loads(request.POST.get('list'))['tags']
            user        = request.user

            if not image:
                return JsonResponse({'MESSAGE' : 'IMAGE_EMPTY'}, status=400)

            with transaction.atomic():
                upload_key = str(uuid.uuid4()) + image.name
                s3_client  = boto3.client(
                    's3',
                    aws_access_key_id     = AWS_S3_ACCESS_KEY_ID,
                    aws_secret_access_key = AWS_S3_SECRET_ACCESS_KEY,
                )
            
                posting = Posting.objects.create(
                    content     = content,
                    image_url   = S3_URL + upload_key,
                    design_type = DesignType.objects.get(name=design_type),
                    user        = user
                )

                Tag.objects.bulk_create(
                    Tag(
                        coordinate = (tag['xx'], tag['yy']),
                        posting = posting,
                        product = Product.objects.get(id=tag['product_id'])
                    ) for tag in tags
                )

                s3_client.upload_fileobj(
                    image,
                    AWS_STORAGE_BUCKET_NAME,
                    upload_key,
                    ExtraArgs = {
                        'ContentType' : image.content_type
                    }
                )

            return JsonResponse({'MESSAGE' : 'POSTING_SUCCESS'}, status=200)
        
        except DesignType.DoesNotExist:
            return JsonResponse({'MESSAGE' : 'DESIGN_TYPE_DOES_NOT_EXIST'}, status=400)
        
        except KeyError:
            return JsonResponse({'MESSAGE' : 'KEY_ERROR'}, status=400)

class BookmarkView(View):
    @SignInDecorator
    def post(self, request, posting_id):
        if not Posting.objects.filter(id=posting_id).exists():
            return JsonResponse({'MESSAGE' : 'POSTING_DOES_NOT_EXIST'}, status=400)

        bookmark, flag = Bookmark.objects.get_or_create(
            posting = Posting.objects.get(id=posting_id),
            user    = request.user
        )

        if not flag:
            bookmark.delete()
            return JsonResponse({'MESSAGE' : 'BOOKMARK_DELETED'}, status=204)
        
        return JsonResponse({'MESSAGE' : 'BOOKMARK_CREATED'}, status=201)

    def get(self, request, user_id):
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({'MESSAGE' : 'USER_DOES_NOT_EXIST'}, status=400)

        bookmarks = Bookmark.objects.select_related('posting', 'user').filter(user_id=user_id)

        bookmark_list = [{
            'posting_id'       : bookmark.posting.id,
            'posting_username' : bookmark.user.nickname,
            'posting_image_url': bookmark.posting.image_url,
        } for bookmark in bookmarks ]

        return JsonResponse({'LIST' : bookmark_list}, status=200)