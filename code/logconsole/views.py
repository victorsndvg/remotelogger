import os
import logging
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import Context, Template
from django.http import HttpResponse
from remotelogger.mongo import Log, StorageInfo

logger = logging.getLogger(__name__)

basedir = os.path.dirname(os.path.realpath(__file__))

def index(request):
    return HttpResponse(open(os.path.join(basedir, 'templates/index.html')))

def users(request):
    users = StorageInfo(logger).list_databases()
    context = {"USERS": users}
    return render(request, 'users.html', context)

def workflows(request, exchange):
    workflows = StorageInfo(logger).list_collections(exchange)
    context = {"WORKFLOWS": workflows}
    return render(request, 'workflows.html', context)

def jobs(request, exchange, routing_key):
    jobs = StorageInfo(logger).list_documents(exchange, routing_key)
    context = {"JOBS": jobs}
    return render(request, 'jobs.html', context)

def logs(request, exchange, routing_key, queue):
    log = Log(exchange=exchange, routing_key=routing_key, queue=queue, logger=logger)
    history = log.get()
    context = {"USER": exchange, "ROOM": routing_key, "NAMESPACE": queue, "HISTORY": history}
    return render(request, 'logs.html', context)
