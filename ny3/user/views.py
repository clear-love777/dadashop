import json
from urllib.parse import urlencode

import requests
from django.core.mail import send_mail
import hashlib
from ntoken.views import make_token
from user.tasks import send_active_email
from .models import UserProfile, Address,WeiBoUser
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection
import random,base64
from django.db import transaction
from tools.logging_check import logging_check
from django.views.generic.base import View
from django.conf import settings
#获取settings中的配置


#本模块下 响应异常状态码 10101 - 10199

# Create your views here.
def user_view(request):
    if request.method=="POST":
        #创建资源
        #前端json串{"uname":"asdasd","password":"asdasd","phone":"131313131313","email":"dada@tedu.cn"}:
        #基础校验[数据给没给,用户名是否可用]
        #{"code":200,"username":username,"token":token}
        #{"code":10101,"error":"The username is already existed"}
        msg=json.loads(request.body.decode())
        uname=msg.get("uname")
        password=msg.get("password")
        phone=msg.get("phone")
        email=msg.get("email")
        print("姓名:",uname)
        print("密码:",password)
        print("电话:",phone)
        print("邮箱:",email)
        if  not uname:
            result={"code":10101,"error":"Please give me username"}
            print("result:",JsonResponse(result))
            return JsonResponse(result)
        if  not password:
            result={"code":10102,"error":"Please give me password"}
            return JsonResponse(result)
        if  not phone:
            result={"code":10103,"error":"Please give me phone"}
            return JsonResponse(result)
        if  not email:
            result={"code":10104,"error":"Please give me email"}
            return JsonResponse(result)
        old_users=UserProfile.objects.filter(username=uname)
        if old_users:
            result={"code":10105,"error":"The username is already registed"}
            return JsonResponse(result)
        m=hashlib.md5()
        m.update(password.encode())
        try:
            UserProfile.objects.create(username=uname,email=email,
                                       phone=phone,password=m.hexdigest())
        except Exception as e:
            print("---create user error")
            print(e)
            result={"code":10106,"error":"The username is already registed"}
            return JsonResponse(result)
        #生成随机码
        random_num=random.randint(1000,9999)
        random_str=uname+"_"+str(random_num)
        #最终链接上的code为
        code_str=base64.urlsafe_b64encode(random_str.encode())
        #随机码存入缓存,用于激活时,后端进行校验
        r=get_redis_connection("verify_email")
        r.set("verify_email_%s"%(uname),random_num)

        active_url="http://127.0.0.1:7001/dadashop/templates/active.html?code=%s"%code_str.decode()
        print("----active_url is ----")
        print(active_url)
        # 执行发邮件[同步]
        # send_active_email(email,active_url)
        #发邮件[异步]
        send_active_email.delay(email,active_url)

        # 默认当前用户已登录[签发token-自定义/官方]
        token=make_token(uname)
        result={"code":200,"username":uname,"data":{"token":token}}
        return JsonResponse(result)
    elif request.method=="GET":
        #获取资源
        pass
    return JsonResponse({"code":200})



def active_view(request):
    #用户激活操作
    if request.method!="GET":
        result={"code":10104,"error":"please use GET"}
        return JsonResponse(result)
    code=request.GET.get("code")
    if not code:
        result = {"code": 10105, "error": "code is not exist"}
        return JsonResponse(result)
        #b64反解 拿到 用户名以及对应的随机码
    try:
        code_str=base64.urlsafe_b64decode(code.encode())
        last_code_str=code_str.decode()
        username,rcode=last_code_str.split("_")
    except Exception as e:
        print("---urlb64 decode error")
        print(e)
        result={"code":10106,"error":"Your code is wrong"}
        return JsonResponse(result)
    #redis中 根据用户名获取到 当初存储的随机码
    r = get_redis_connection("verify_email")
    old_code=r.get("verify_email_%s"%username)
    if not old_code:
        result={"code":10107,"error":"Your code is wrong"}
        return JsonResponse(result)
    if rcode!=old_code.decode():
        result={"code":10108,"error":"Your code is wrong"}
        return JsonResponse(result)
    try:
        user=UserProfile.objects.get(username=username,isActive=False)
    except Exception as e:
        result={"code":10109,"error":"Your is already actived"}
        return JsonResponse(result)
    # 两个随机码进行比对,如果一致,将用户名对应的用户数据isActive=True
    user.isActive=True
    user.save()
    #redis缓存中 删除对应数据
    r.delete("verify_email_%s"%username)

    return JsonResponse({"code":200,"data":{"message":"激活成功"}})

class AddressView(View):
    #CBV - class base view 基于类的视图
    #FBV - function base view 基于函数的视图
    #   1,class继承View;
    #   2,urls中 关联视图类时,需要按如下绑定:
    #url(r"^/(?P<username>\w{1,11})/address$",views.AddressView.as_view()),

    @logging_check
    def get(self,request,username):
        user=request.myuser
        if user.username!=username:
            result={"code":10111,"error":"Yor URL is error"}
            return JsonResponse(result)
        all_address=Address.objects.filter(user=user,isActive=True)
        all_address_list=[]
        for add in all_address:
            d={}
            d["id"]=add.id
            d["receiver"]=add.receiver
            d["address"]=add.address
            d["receiver_mobile"]=add.receiver_mobile
            d["postcode"]=add.postcode
            d["tag"]=add.tag
            d["isDefault"]=add.isDefault
            all_address_list.append(d)
        return JsonResponse({"code":200,"addresslist":all_address_list})
    @logging_check
    def post(self,request,username):
        """
        address: "北京市北京市市辖区东城区asd"
        postcode: "111111"
        receiver: "asd"
        receiver_phone: "13131313131"
        tag: "家"
            """
        user=request.myuser
        print("ssss:",user)
        if user.username!=username:
            result={"code":10110,"error":"Your url is error"}
            return JsonResponse(result)
        json_str=request.body
        json_obj=json.loads(json_str)
        receiver=json_obj.get("receiver")
        address=json_obj.get("address")
        receiver_phone=json_obj.get("receiver_phone")
        postcode=json_obj.get("postcode")
        tag=json_obj.get("tag")
        old_address=Address.objects.filter(user=user)
        #判断是否为第一次添加地址[如果是第一次添加,则设置当前地址为默认地址]
        isFiirst=False
        if not old_address:
            isFiirst=True
        Address.objects.create(user=user,receiver=receiver,address=address,
                               receiver_mobile=receiver_phone,postcode=postcode,
                               tag=tag,isDefault=isFiirst)
        return JsonResponse({"code":200,"data":"新增地址成功"})

    @logging_check
    def put(self,request,username,id):
        #更新地址
        #将前端传来的修改值同步到数据库
        user = request.myuser
        if user.username != username:
            result = {"code": 10111, "error": "Your url is error"}
            return JsonResponse(result)
        json_str=request.body
        json_obj=json.loads(json_str)
        my_id=json_obj.get("id")
        if int(id)!=int(my_id):
            print("zzzzzzzzzzz")
            result={"code":10112,"error":"Your url is error"}
            return JsonResponse(result)
        """
        address: "北京市北京市市辖区东城区asdasd"
        id: 1
        receiver: "aaa"
        receiver_mobile: "13131313132"
        tag: "家"
        """
        receiver = json_obj.get("receiver")
        my_address = json_obj.get("address")
        receiver_mobile = json_obj.get("receiver_mobile")
        tag = json_obj.get("tag")
        try:
            address=Address.objects.get(user=user,id=id,isActive=True)
        except Exception as e:
            result={"code":10113,"error":"Your id is error"}
            return JsonResponse(result)
        address.receiver=receiver
        address.address=my_address
        address.receiver_mobile=receiver_mobile
        address.tag=tag
        address.save()
        return JsonResponse({"code": 200,"data":"修改成功"})
    @logging_check
    def delete(self,request,username,id):
        #删除地址
        #将对应的地址数据中isActive=False
        user = request.myuser
        if user.username != username:
            result = {"code": 10115, "error": "Your url is error"}
            return JsonResponse(result)
        try:
            address=Address.objects.get(user=request.myuser,id=id)
        except Exception as e:
            result={"code":10114,"error":"The id is error"}
            return JsonResponse(result)
        #默认地址 不可删除
        address.isActive=False
        address.save()
        return JsonResponse({"code":200,"data":"删除成功"})
def get_weibo_login_url():
    #生成微博授权登录页面地址
    #如果需要高级权限 需要在此声明 scope 详情见笔记
    params={"response_type":"code",
            "client_id":settings.WEIBO_CLIENT_ID,
            "redirect_uri":settings.WEIBO_RETURN_URL,}
    login_url="https://api.weibo.com/oauth2/authorize?"
    url=login_url+urlencode(params)
    return url
def weibo_login(request):
    url=get_weibo_login_url()
    return JsonResponse({"code":200,"oauth_url":url})


class WeiBoView(View):
    def get(self,request):
        code=request.GET.get("code")
        #向微博服务器发送请求,用code交换token
        result=get_access_token(code)
        print("----exchange token result is")
        print(result)
        """
        {
        'access_token': '2.00PuxgGG1NwD7Ca5c49fde53OBcZLC', 
        'remind_in': '157679999',
        'expires_in': 157679999, 
        'uid': '5595695067', 
        'isRealName': 'true'
        }
        """
        #WeiBoUser表中是否有这个 weibo用户数据
        #如果没有数据,第一次访问->创建WeiBoUser数据
        #有的话,1)绑定注册过[uid有值]->签发自己的token
        # 2)没绑定[uid为空]->给前端返回非200的code,触发绑定注册
        wuid=result.get("uid")
        access_token=result.get("access_token")
        #查询weibo用户表,判断是否为第一次光临
        try:
            weibo_user=WeiBoUser.objects.get(wuid=wuid)
        except Exception as e:
            #没数据-该微博账号第一次登录
            WeiBoUser.objects.create(wuid=wuid,access_token=access_token)
            result={"code":201,"uid":wuid}
            return  JsonResponse(result)
        else:
            #非第一次登录 [WeiBoUser表里 有当前wuid对应的数据]
            uid=weibo_user.uid
            if uid:
                #之前已经绑定注册过 我们网站的用户
                username=uid.username
                token=make_token(username)
                result={"code":200,"username":username,"data":{"token":token}}
                return JsonResponse(result)
            else:
                #之前用当前微博账号登录过,但是没有完成后续的绑定注册流程
                result={"code":201,"uid":wuid}
                return JsonResponse(result)
    def post(self,request):
        #绑定注册
        """
                email: "490159632@qq.com"
                password: "123456"
                phone: "13997721339"
                uid: "5595695067"
                username: "xixi"
        """
        json_str=request.body.decode()
        json_obj=json.loads(json_str)
        username=json_obj.get("username")
        password=json_obj.get("password")
        phone=json_obj.get("phone")
        email=json_obj.get("email")
        wuid=json_obj.get("uid")
        if  not username:
            result={"code":10101,"error":"Please give me username"}
            print("result:",JsonResponse(result))
            return JsonResponse(result)
        if  not password:
            result={"code":10102,"error":"Please give me password"}
            return JsonResponse(result)
        if  not phone:
            result={"code":10103,"error":"Please give me phone"}
            return JsonResponse(result)
        if  not email:
            result={"code":10104,"error":"Please give me email"}
            return JsonResponse(result)
        old_users=UserProfile.objects.filter(username=username)
        if old_users:
            result={"code":10105,"error":"The username is already registed"}
            return JsonResponse(result)


        m = hashlib.md5()
        m.update(password.encode())
        password_m=m.hexdigest()
        try:
            with transaction.atomic():
                #创建UserProfile用户数据
                user=UserProfile.objects.create(username=username, email=email,
                                           phone=phone, password=password_m)
                weibo_user=WeiBoUser.objects.get(wuid=wuid)
                #绑定外键
                weibo_user.uid=user
                weibo_user.save()
        except Exception as e:
            print("---bind user weibouser")
            result={"code":10116,"error":"The username is already existed!"}
            return JsonResponse(result)
        # 生成随机码
        random_num = random.randint(1000, 9999)
        random_str = username + "_" + str(random_num)
        # 最终链接上的code为
        code_str = base64.urlsafe_b64encode(random_str.encode())
        # 随机码存入缓存,用于激活时,后端进行校验
        r = get_redis_connection("verify_email")
        r.set("verify_email_%s" % (username), random_num)

        active_url = "http://127.0.0.1:7001/dadashop/templates/active.html?code=%s" % code_str.decode()
        print("----active_url is ----")
        print(active_url)
        # 执行发邮件[同步]
        # send_active_email(email,active_url)
        # 发邮件[异步]
        send_active_email.delay(email, active_url)

        # 默认当前用户已登录[签发token-自定义/官方]
        token = make_token(username)
        result = {"code": 200, "username": username, "data": {"token": token}}
        return JsonResponse(result)
def get_access_token(code):
    #向第三方认证服务器发送code 交换token
    token_url="https://api.weibo.com/oauth2/access_token"
    #post 请求
    post_data={
        "client_id":settings.WEIBO_CLIENT_ID,
        "client_secret":settings.WEIBO_CLIENT_SECRET,
        "grant_type":"authorization_code",
        "redirect_uri": settings.WEIBO_RETURN_URL,
        "code":code
    }
    try:
        res=requests.post(token_url,data=post_data)
    except Exception as e:
        print("---weibo exchange error")
        print(e)
        return None
    if res.status_code==200:
        return json.loads(res.text)
    return None