from django.db import models


class UserInfo(models.Model):
    user = models.OneToOneField('register.User', on_delete=models.CASCADE)
    motive = models.TextField()


class JobHistory(models.Model):
    user_info = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    history = models.CharField(max_length=255)
