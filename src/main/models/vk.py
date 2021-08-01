import os

from django.db import models
from djchoices import DjangoChoices, ChoiceItem

from main.models.base import BaseModel
from .user import User


class Gender(DjangoChoices):
    male = ChoiceItem('male', 'мужчина')
    female = ChoiceItem('female', 'женщина')


class VkTask(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parse_group = models.CharField(max_length=255, null=True, blank=True)
    parse_group_model = models.ForeignKey("VkGroup", on_delete=models.SET_NULL, null=True, blank=True)

    parse_user = models.CharField(max_length=255, null=True, blank=True)
    parse_user_model = models.ForeignKey("VkUser", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'vk_task'


class VkGroup(BaseModel):
    id = models.BigIntegerField(primary_key=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    members_count = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'vk_group'


class VkUser(BaseModel):
    id = models.BigIntegerField(primary_key=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    age_after_ml = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(choices=Gender.choices, null=True, blank=True)
    gender_after_ml = models.CharField(choices=Gender.choices, null=True, blank=True)
    proceed = models.BooleanField(default=False, blank=True)
    is_closed = models.BooleanField(default=False, null=True, blank=True)

    friends = models.ManyToManyField('VkUser', related_name='friends')
    groups = models.ManyToManyField('VkGroup', related_name='own_groups')

    class Meta:
        db_table = 'vk_user'


def image_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    if instance.photo_id is not None:
        return f"{instance.vk_user.id}/{instance.photo_id}/{file_extension}"
    return f"{instance.vk_user.id}/{instance.vk_user.id}__%f/{file_extension}"


class VKPhoto(models.Model):
    photo_id = models.CharField(max_length=100, null=True, blank=True)
    vk_user = models.ForeignKey(VkUser, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_path)
    link = models.URLField()
    is_avatar = models.BooleanField(default=False)
    likes = models.IntegerField(null=True, blank=True)
    comments = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'vk_photo'
