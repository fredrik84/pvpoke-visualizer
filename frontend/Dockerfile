FROM python:3.7-alpine
ENV FLASK_APP=app.py

WORKDIR /app
ADD app/requirements.txt /app/
RUN pip install -r /app/requirements.txt
ADD app/ /app/
RUN mkdir /data
RUN ln -s /data /app/templates/scenarios

ENTRYPOINT flask run -h 0.0.0.0
