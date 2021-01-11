from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver



def ava_path(instance, filename):
    return 'user_{0}/avas/{1}'.format(instance.user.id, filename)


def add_path(instance, filename):
    return 'user_{0}/posts/{1}'.format(instance.author.id, filename)


class Profile(models.Model):
    '''
    Модель пользователя
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    birth_date = models.DateField('Date of birth', null=True, blank=True)
    about = models.TextField('About', max_length=500, blank=True)
    ava = models.ImageField(upload_to=ava_path, default=None)
    phone_number = models.CharField(max_length=12, default=None)

    def __str__(self):
        return str(self.user.username)


class Category(models.Model):
    name = models.TextField(max_length=64, verbose_name='название')

    def __str__(self):
        return str(self.name)


class Add(models.Model):
    '''
    Объявление
    '''
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    header = models.TextField(max_length=100)
    description = models.TextField(max_length=1000, blank=True)
    image = models.ImageField(upload_to=add_path)
    date_pub = models.DateTimeField(auto_now_add=True)
    date_edit = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='категория')

    def __str__(self):
        return 'Author {} date {}'.format(self.author.username, self.date_pub)


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.user_profile.save()


class Comment(models.Model):
    """
    Коментарий к посту
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    text = models.TextField(max_length=700, blank=False)
    in_post = models.ForeignKey(Add, on_delete=models.CASCADE)
    date_publish = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{0} : {1}".format(self.author, self.text[:10] + "...")