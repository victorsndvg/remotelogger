import os
import logging
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import Context, Template
from django.http import HttpResponse
from remotelogger.mongo import Log

logger = logging.getLogger(__name__)

basedir = os.path.dirname(os.path.realpath(__file__))

def index(request):
    return HttpResponse(open(os.path.join(basedir, 'templates/index.html')))

def logs(request, user, room, namespace):
    log = Log(exchange=user, routing_key=room, queue=namespace, logger=logger)
    history = log.get()
    context = {"USER": user, "ROOM": room, "NAMESPACE": namespace, "HISTORY": history}
    return render(request, 'index.html', context)
