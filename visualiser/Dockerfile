FROM python:3.7-alpine
ENV FLASK_APP=app.py

WORKDIR /data
ADD app/requirements.txt /data/
RUN pip install -r /data/requirements.txt
ADD app/ /data/


ENTRYPOINT flask run -h 0.0.0.0
