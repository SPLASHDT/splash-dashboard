FROM python:3.13.2-alpine3.21


RUN mkdir /splash-dashboard && \
apk update && \
apk add gcc musl-dev linux-headers

COPY requirements.txt /splash-dashboard
RUN cd /splash-dashboard && pip install -r requirements.txt
COPY . /splash-dashboard
ENV SPLASH_ENV=docker
ENTRYPOINT cd /splash-dashboard && python dashboard.py
EXPOSE 8050
