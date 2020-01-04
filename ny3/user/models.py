from django.db import models

# Create your models here.
class UserProfile(models.Model):
    username=models.CharField("用户名",max_length=11,unique=True)
    password=models.CharField("密码",max_length=32)
    email=models.EmailField()
    phone=models.CharField("手机号",max_length=11)
    isActive=models.BooleanField("是否激活",default=False)
    create_time=models.DateTimeField(auto_now_add=True)
    update_time=models.DateTimeField(auto_now=True)
    class Meta:
        db_table="user_profile"
    def __str__(self):
        return "%s_%s"%(self.username,self.isActive)
class Address(models.Model):
    receiver=models.CharField(max_length=11,verbose_name="收件人")
    address=models.CharField(max_length=100,verbose_name="收件地址")
    postcode=models.CharField(max_length=6,verbose_name="邮编")
    receiver_mobile=models.CharField(max_length=11,verbose_name="收件人手机号")
    tag=models.CharField(max_length=11,verbose_name="标签")
    isDefault=models.BooleanField(default=False,verbose_name="是否为默认地址")
    isActive=models.BooleanField(default=True,verbose_name="是否为活跃地址")
    created_time=models.DateTimeField(auto_now_add=True)
    updated_time=models.DateTimeField(auto_now=True)
    user=models.ForeignKey(UserProfile)
    class Meta:
        db_table="address"
    def __str__(self):
        return "%s_%s_%s_%s"%(self.id,self.receiver,self.address,self.receiver_mobile)
class WeiBoUser(models.Model):
    uid=models.OneToOneField(UserProfile,null=True)
    wuid=models.CharField(max_length=50,db_index=True)
    access_token=models.CharField(max_length=100)

    class Meta:
        db_table="weibo_user"
    def __str__(self):
        return "%s_%s"%(self.uid,self.wuid)
