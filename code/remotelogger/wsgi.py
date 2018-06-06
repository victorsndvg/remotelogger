"""
WSGI config for remotelogger project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "remotelogger.settings")

from django.core.wsgi import get_wsgi_application

from socketio import Middleware
from remotelogger.sio import sio

#application = get_wsgi_application()

django_app = get_wsgi_application()
application = Middleware(sio, django_app)
