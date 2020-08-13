from django.db import models


class LineInputData(models.Model):
    QUESTIONS_NAME = (
        ('name', '名前'),
        ('history', '職歴'),
        ('motive', '志望動機'),
    )
    user_id = models.CharField(max_length=255)
    question = models.CharField(max_length=30, choices=QUESTIONS_NAME)
    answer = models.TextField()
    message = models.JSONField()  # JSONフィールドはDBによって使えないものもあるかも
    timestamp = models.DateField()
