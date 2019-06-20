FROM python:3.6-alpine

WORKDIR /data
add requirements.txt /data/
ADD app/ /data/
ADD bin/ /usr/bin/

RUN pip3 install -r requirements.txt
RUN apk --no-cache add --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing firefox

ENTRYPOINT python test.py


