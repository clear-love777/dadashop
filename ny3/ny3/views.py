import json

from django.http import HttpResponse
from django.shortcuts import render


def test_cors(request):
    return render(request,"index.html")

def test_cors_server(request):
    # ds=json.dumps({"msg":"哈哈哈哈"})
    msg=request.POST.get("msg")

    return HttpResponse(json.dumps({"msg":msg}),content_type="application/json")