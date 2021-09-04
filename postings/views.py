import boto3, uuid, json

from django.http           import JsonResponse
from django.views          import View
from django.db             import transaction
from django.db.models      import Prefetch
from django.core.paginator import Paginator

from postings.models          import Posting, DesignType, Tag, Comment
from homestagram.settings     import AWS_STORAGE_BUCKET_NAME, AWS_S3_SECRET_ACCESS_KEY, AWS_S3_ACCESS_KEY_ID, S3_URL
from users.utils              import SignInDecorator
from users.models             import Bookmark, Follow
from products.models          import Product
from decorators               import query_debugger

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

    # @SignInDecorator
    # def delete(self, request, posting_id):
    #     user = request.user
    #     Tag.objects.filter(posting_id=posting_id).delete()
    #     Bookmark.objects.filter(posting_id=posting_id).delete()
    #     Comment.objects.filter(posting_id=posting_id).delete()
    #     Posting.objects.filter(id=posting_id).delete()

    #     return JsonResponse({'MESSAGE' : 'POSTING_DELETED'}, status=200)

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

    @SignInDecorator
    def get(self, request):
        user = request.user

        bookmarks = Bookmark.objects.select_related('posting', 'posting__user').filter(user_id=user.id)

        bookmark_list = [{
            'posting_id'       : bookmark.posting.id,
            'posting_username' : bookmark.posting.user.nickname,
            'posting_image_url': bookmark.posting.image_url,
        } for bookmark in bookmarks ]

        return JsonResponse({'LIST' : bookmark_list}, status=200)

class CommentView(View):
    @SignInDecorator
    def post(self, request, posting_id):
        try:
            if not Posting.objects.filter(id=posting_id).exists():
                return JsonResponse({'MESSAGE' : 'POSTING_DOES_NOT_EXIST'})

            data = json.loads(request.body)

            Comment.objects.create(
                content = data['content'],
                user = request.user,
                posting_id = posting_id
            )

            return JsonResponse({'MESSAGE' : 'COMMENT_CREATED'}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE' : 'KEY_ERROR'}, status=400)

    def patch(self, request, comment_id):
        if not Comment.objects.filter(id=comment_id).exists():
            return JsonResponse({'MESSAGE' : 'COMMENT_DOES_NOT_EXIST'})

        data = json.loads(request.body)

        Comment.objects.filter(id=comment_id).update(
            content = data['content']
        )

        return JsonResponse({'MESSAGE' : 'COMMENT_EDITED'}, status=200)

    def delete(self, request, comment_id):
        if not Comment.objects.filter(id=comment_id).exists():
            return JsonResponse({'MESSAGE' : 'COMMENT_DOES_NOT_EXIST'})

        Comment.objects.filter(id=comment_id).delete()

        return JsonResponse({'MESSAGE' : 'COMMENT_DELETED'}, status=200)

class PostingFeedPublicView(View):
    def get(self, request):
        page      = int(request.GET.get('page', 1))
        postings  = Posting.objects.select_related('user').prefetch_related('comment_set', 'comment_set__user', 'tag_set', 'tag_set__product').order_by('-created_at')

        feed = [{
            'feedId'    : posting.id,
            'feeduserId': posting.user.id,
            'feedUserName' : posting.user.nickname,
            'src'       : posting.image_url,
            'content'   : posting.content,
            'postedDate': str(posting.created_at)[:10],
            'designType': posting.design_type_id,
            'comment'   : [{
                'id'       : comment.id,
                'content'  : comment.content,
                'date'     : str(comment.created_at)[:10],
                'user_name': comment.user.nickname
            } for comment in posting.comment_set.all()],
            'tags' : [{
                'id'           : tag.id,
                'product_id'   : tag.product.id,
                'xx'           : int(tag.coordinate.lstrip('(').rstrip(')').split(',')[0]),
                'yy'           : int(tag.coordinate.lstrip('(').rstrip(')').split(',')[1]),
                'product_title': tag.product.product_name,
                'product_price': round(tag.product.price),
                'thumbnail_url': tag.product.thumbnail_url
            } for tag in posting.tag_set.all()],
            'follow'  : False,
            'bookmark': False
        } for posting in postings ]

        paginator = Paginator(feed, 5)
        pages     = paginator.get_page(page).object_list
        has_next  = paginator.get_page(page).has_next()

        return JsonResponse({
            'POSTING_FEED': pages,
            'HAS_NEXT'    : has_next
            })

class PostingFeedPrivateView(View):
    @SignInDecorator
    @query_debugger
    def get(self, request):
        page      = int(request.GET.get('page', 1))
        user      = request.user
        bookmarks = Bookmark.objects.filter(user_id=user.id)
        followers = Follow.objects.filter(follower_id=user.id)
        postings  = Posting.objects.select_related('user').prefetch_related('comment_set',\
                    'comment_set__user', 'tag_set', 'tag_set__product', Prefetch('bookmark_set',\
                    queryset=bookmarks), Prefetch('user__followed',queryset=followers)).\
                    order_by('-created_at')

        feed = [{
            'feedId'      : posting.id,
            'feeduserId'  : posting.user.id,
            'feedUserName': posting.user.nickname,
            'src'         : posting.image_url,
            'content'     : posting.content,
            'postedDate'  : str(posting.created_at)[:10],
            'designType'  : posting.design_type_id,
            'comment'     : [{
                'id'       : comment.id,
                'content'  : comment.content,
                'date'     : str(comment.created_at)[:10],
                'user_name': comment.user.nickname
            } for comment in posting.comment_set.all()],
            'tags' : [{
                'id'           : tag.id,
                'product_id'   : tag.product.id,
                'xx'           : int(tag.coordinate.lstrip('(').rstrip(')').split(',')[0]),
                'yy'           : int(tag.coordinate.lstrip('(').rstrip(')').split(',')[1]),
                'product_title': tag.product.product_name,
                'product_price': round(tag.product.price),
                'thumbnail_url': tag.product.thumbnail_url
            } for tag in posting.tag_set.all()],
            'follow'  : posting.user.followed.exists(),
            'bookmark': posting.bookmark_set.exists()
        } for posting in postings ]

        paginator = Paginator(feed, 5)
        pages     = paginator.get_page(page).object_list
        has_next  = paginator.get_page(page).has_next()

        return JsonResponse({
            'POSTING_FEED': pages,
            'HAS_NEXT'    : has_next
            })