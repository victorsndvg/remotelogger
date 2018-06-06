import os
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import Context, Template
from django.http import HttpResponse

basedir = os.path.dirname(os.path.realpath(__file__))

def index(request):
    return HttpResponse(open(os.path.join(basedir, 'templates/index.html')))

def logs(request, namespace):
    print(namespace)
    context = {"NAMESPACE": namespace}
    return render(request, 'index.html', context)
