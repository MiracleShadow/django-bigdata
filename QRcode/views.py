from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from datetime import datetime
from django.db import connection
import qrcode


def discovery_view(request):
    if request.method == 'GET':
        print("GET")
        return render(request, 'discovery.html')
    else:
        print("POST")
        text = request.POST.get("textarea")
        img = qrcode.make(text)
        context = {
            'text': text,
            'img': img
        }
        img.save("static/image/%s.png" % text)
        return render(request, 'discovery.html', context=context)
