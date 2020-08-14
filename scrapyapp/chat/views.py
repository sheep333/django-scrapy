from django.http import Http404

from .line import LineBotModule


def line_callback(request):
    if request.method != "POST":
        raise Http404
    LineBotModule(request)
    return 'OK'
