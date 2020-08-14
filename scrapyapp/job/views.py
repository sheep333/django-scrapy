from django.views.generic import CreateView

from .models import UserInfo


class UserInfoCreate(CreateView):
    model = UserInfo
