import json, jwt, requests

from django.views import View
from django.http  import JsonResponse

from users.models import User
from my_settings  import SECRET_KEY

class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            kakao_access_token = data['access_token']
            kakao_user_info = requests.get('https://kapi.kakao.com/v2/user/me', headers={'Authorization':f'Bearer {kakao_access_token}'}).json()

            kakao_id = kakao_user_info.get('id', None)

            if not kakao_id:
                return JsonResponse({'MESSAGE':'INVALID_KAKAO_TOKEN'}, status=400)

            kakao_email = kakao_user_info['kakao_account'].get('email', None)

            if not kakao_email:
                if kakao_user_info['kakao_account']['email_needs_agreement']:
                    return JsonResponse({'MESSAGE':'NEED_EMAIL_AGREEMENT'}, status=400)

                return JsonResponse({'MESSAGE':'INVALID_KAKAO_TOKEN'}, status=400)

            if User.objects.filter(nickname=data['nickname']).exists():
                return JsonResponse({'MESSAGE':'NICKNAME_ALREADY_EXISTS'}, status=409)

            User.objects.create(
                kakao_id    = kakao_user_info['id'],
                kakao_email = kakao_user_info['kakao_account']['email'],
                nickname    = data['nickname'],
            )

            return JsonResponse({'MESSAGE':'SIGN_UP_SUCCESS'}, status=201)

        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status=400)