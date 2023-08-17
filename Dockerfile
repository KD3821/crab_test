FROM python:3.9-slim

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libpq-dev postgresql-client

RUN useradd -rms /bin/bash quiz_user && chmod 777 /opt /run

WORKDIR /quiz_app/

RUN mkdir /quiz_app/media && chown -R quiz_user:quiz_user /quiz_app && chmod 755 /quiz_app

COPY --chown=quiz_user:quiz_user . .

RUN pip install -r requirements.txt

USER quiz_user

CMD ["gunicorn","-b","0.0.0.0:8001","tests_app.wsgi:application"]
