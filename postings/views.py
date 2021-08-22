import boto3, uuid

from django.http  import JsonResponse
from django.views import View

from postings.models          import Posting, DesignType
from homestagram.settings     import AWS_STORAGE_BUCKET_NAME, AWS_S3_SECRET_ACCESS_KEY, AWS_S3_ACCESS_KEY_ID
from users.utils              import SignInDecorator
from users.models             import Bookmark, User

class PostingView(View):
    @SignInDecorator
    def post(self, request):
        try:
            content     = request.POST.get('content')
            design_type = request.POST.get('design_type')
            image       = request.FILES.get('image')
            
            if not image:
                return JsonResponse({'MESSAGE' : 'IMAGE_EMPTY'}, status=400)

            upload_key = str(uuid.uuid4()) + image.name
            s3_client  = boto3.client(
                's3',
                aws_access_key_id     = AWS_S3_ACCESS_KEY_ID,
                aws_secret_access_key = AWS_S3_SECRET_ACCESS_KEY,
            )
            
            Posting.objects.create(
                content     = content,
                image_url   = 'https://homestagram.s3.ap-northeast-2.amazonaws.com/' + upload_key,
                design_type = DesignType.objects.get(name=design_type),
                user        = request.user
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