FROM python:3.7-alpine

WORKDIR /app
ADD app/requirements.txt /app/
RUN pip install -r /app/requirements.txt
ADD app/ /app/
RUN mkdir /data

ENTRYPOINT python app.py
