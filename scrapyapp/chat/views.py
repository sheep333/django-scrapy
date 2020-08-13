from django.shortcuts import render
from django.http import Http404

from .line import LineBotModule


def line_callback(request):
    if request.method == "POST":
        LineBotModule(request)
        return 'OK'
    return Http404
