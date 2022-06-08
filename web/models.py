from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=16, null=False)
    password = models.CharField(max_length=32, null=False)


class File(models.Model):
    filename = models.CharField(max_length=256, null=False)
    file_hash_name = models.CharField(max_length=128, null=False)
    filetype = models.IntegerField(choices=((1, '文件夹'), (0, '文件')), null=False)
    filepath = models.CharField(max_length=256, null=False)
    file_hash = models.CharField(max_length=256, null=False)
    status = models.IntegerField(choices=((1, '正常'), (0, '已删除')))
    parent = models.ForeignKey(to='File', on_delete=models.CASCADE, null=True, default=None)
    create_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to='User', on_delete=models.CASCADE)


class Share(models.Model):
    files = models.ManyToManyField(to='File')
    create_time = models.DateTimeField(auto_now_add=True)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.IntegerField(verbose_name='有限期', choices=period_choices, default=1440)
    creator = models.ForeignKey(verbose_name='创建者', to='User')
    password = models.CharField(max_length=4, null=False)
