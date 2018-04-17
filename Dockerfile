FROM python:3.5  
ENV PYTHONUNBUFFERED 1  
ADD config/requirements.pip /config/  
RUN pip install -r /config/requirements.pip  
RUN mkdir /code;  
WORKDIR /code  
