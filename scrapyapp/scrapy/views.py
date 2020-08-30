from django.shortcuts import render

from .scraping import Register


# Create your views here.
def scrapy_start(request):
    url = 'https;//xxx/xxx.jp'
    register = Register()
    register.start_login(url, request.user.pk)
    register.start_regist(url)
