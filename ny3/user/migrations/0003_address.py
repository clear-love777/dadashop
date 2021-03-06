# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-01-02 08:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20191231_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.CharField(max_length=11, verbose_name='收件人')),
                ('address', models.CharField(max_length=100, verbose_name='收件地址')),
                ('postcode', models.CharField(max_length=6, verbose_name='邮编')),
                ('receiver_mobile', models.CharField(max_length=11, verbose_name='收件人手机号')),
                ('tag', models.CharField(max_length=11, verbose_name='标签')),
                ('isDefault', models.BooleanField(default=False, verbose_name='是否为默认地址')),
                ('isActive', models.BooleanField(default=True, verbose_name='是否为活跃地址')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.UserProfile')),
            ],
            options={
                'db_table': 'address',
            },
        ),
    ]
