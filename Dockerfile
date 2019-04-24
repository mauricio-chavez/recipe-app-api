FROM python:3.7-alpine
LABEL mainteiner "Mauricio Chávez Olea <mauriciochavez@ciencias.unam.mx"

ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt /requirements.txt
RUN apk add --update  --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user
