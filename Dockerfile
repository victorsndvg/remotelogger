FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN useradd uwsgi
RUN useradd celery
RUN mkdir -p /code /config
ADD config/requirements.pip /config/
RUN pip install -r /config/requirements.pip
WORKDIR /code
