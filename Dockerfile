FROM python:3.9.1-alpine

RUN apk add curl
RUN apk add gcc
RUN apk add g++
RUN apk add --no-cache gnupg
RUN apk add unixodbc-dev
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./install.sh .
RUN ./install.sh
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
COPY . .