FROM python:2.7-slim

# from https://github.com/mozmeao/docker-pythode/blob/master/Dockerfile.footer

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# add non-priviledged user
RUN adduser --uid 1000 --disabled-password --gecos '' --no-create-home webdev

# Add apt script
COPY docker/bin/apt-install /usr/local/bin/

# end from Dockerfile.footer

EXPOSE 8000
CMD ["./bin/run-prod.sh"]
WORKDIR /app
ENV DJANGO_SETTINGS_MODULE=nucleus.settings

RUN apt-install build-essential libpq-dev gettext libxslt1.1 libxml2 libxml2-dev libxslt1-dev

COPY requirements.txt /app/
RUN pip install --require-hashes --no-cache-dir -r requirements.txt

COPY . /app
RUN DEBUG=False SECRET_KEY=foo ALLOWED_HOSTS=localhost, DATABASE_URL=sqlite:// ./manage.py collectstatic --noinput

# Change User
RUN chown webdev.webdev -R .
USER webdev
