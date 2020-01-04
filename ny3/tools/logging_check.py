import jwt
from django.http import JsonResponse
from django.conf import settings
from user.models import UserProfile

def logging_check(func):
    def wrapper(self,request,*args,**kwargs):
        token=request.META.get("HTTP_AUTHORIZATION")
        if not token:
            result={"code":10208,"error":"Please login!"}
            return JsonResponse(result)
        try:
            res=jwt.decode(token,settings.JWT_TOKEN_KEY,algorithm="HS256")
        except Exception as e:
            print(e)
            result={"code":10209,"error":"Please login!!"}
            return JsonResponse(result)
        username=res["username"]
        user=UserProfile.objects.get(username=username)
        #将user 赋值给request,方便视图函数获取当前登录用户
        request.myuser=user
        return func(self,request,*args,**kwargs)
    return wrapper