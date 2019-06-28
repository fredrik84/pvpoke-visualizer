FROM python:3.7-alpine
ENV FLASK_APP=app.py

WORKDIR /app
ADD app/requirements.txt /app/
RUN pip install -r /app/requirements.txt
ADD app/ /app/
RUN mkdir /data
RUN ln -s /data /app/static/scenarios

ENTRYPOINT flask run --with-threads -h 0.0.0.0
