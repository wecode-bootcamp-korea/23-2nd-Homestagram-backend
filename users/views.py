import json, jwt, requests

from django.views import View
from django.http  import JsonResponse

from users.models import User
from my_settings  import SECRET_KEY, ALGORITHM

class SocialSignInView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            kakao_access_token = data['access_token']
            kakao_user_info = requests.get('https://kapi.kakao.com/v2/user/me', headers={'Authorization':f'Bearer {kakao_access_token}'}).json()

            kakao_id = kakao_user_info.get('id', None)

            if not kakao_id:
                return JsonResponse({'MESSAGE':'INVALID_KAKAO_TOKEN'}, status=400)

            kakao_email = kakao_user_info['kakao_account'].get('email', None)

            user, is_created = User.objects.get_or_create(kakao_id=kakao_id, kakao_email=kakao_email)

            access_token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm=ALGORITHM)

            return JsonResponse(
                {
                    'token'   : access_token,
                    'user_id' : user.id,
                    'nickname': user.nickname if user.nickname else None,
                    'email'   : user.kakao_email
            }, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)