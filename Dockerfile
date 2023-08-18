FROM python:3.9-slim

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libpq-dev postgresql-client

WORKDIR /quiz_app/

COPY . /quiz_app/

RUN mkdir /quiz_app/media && chmod o+r -R /quiz_app

RUN pip install -r requirements.txt

CMD ["gunicorn","-b","0.0.0.0:8001","tests_app.wsgi:application"]
