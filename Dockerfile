FROM quay.io/mozmar/ubuntu-slim-python:latest

EXPOSE 8000
CMD ["./bin/run-prod.sh"]

RUN adduser --uid 1000 --disabled-password --gecos '' --no-create-home webdev
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential python python-dev python-pip python-setuptools \
        libpq-dev postgresql-client python-psycopg2 gettext && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV DJANGO_SETTINGS_MODULE=nucleus.settings
ENV LANG=C.UTF-8

COPY requirements.txt /app/requirements.txt
RUN pip install --require-hashes --no-cache-dir --ignore-installed -r requirements.txt

COPY . /app
RUN DEBUG=False SECRET_KEY=foo ALLOWED_HOSTS=localhost, DATABASE_URL=sqlite:// ./manage.py collectstatic --noinput

# Change User
RUN chown webdev.webdev -R .
USER webdev
