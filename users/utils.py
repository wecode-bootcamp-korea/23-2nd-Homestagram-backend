import jwt

from django.http.response   import JsonResponse

from my_settings            import ALGORITHM
from users.models           import User
from homestagram.settings   import SECRET_KEY


class SignInDecorator: 
    def __init__(self, function):
        self.function = function

    def __call__(self, request, *args, **kwargs):
        token = request.headers.get("Authorization", None)
        
        try:
            if token:
                payload       = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
                request.user  = User.objects.get(id = payload["id"])

                if not request.user.nickname:
                    return JsonResponse({"MESSAGE":"NEED_NICKNAME"}, status=401)

                return self.function(self, request, *args, **kwargs)   

            return JsonResponse({"MESSAGE":"NEED_LOGIN"}, status=401)

        except jwt.DecodeError:
            return JsonResponse({"MESSAGE":"INVALID_TOKEN"}, status=401)