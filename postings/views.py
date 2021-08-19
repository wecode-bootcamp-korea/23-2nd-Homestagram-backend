import boto3, uuid

from django.http  import JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist

from postings.models          import Posting, DesignType
from homestagram.settings     import AWS_STORAGE_BUCKET_NAME, AWS_S3_SECRET_ACCESS_KEY, AWS_S3_ACCESS_KEY_ID
from users.utils              import SignInDecorator

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
