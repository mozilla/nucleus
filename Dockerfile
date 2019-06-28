# BUILDER IMAGE
FROM python:3.7-slim-stretch AS builder

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=nucleus.settings
WORKDIR /app
RUN python -m venv /venv

# Add apt script
COPY docker/bin/apt-install /usr/local/bin/
RUN apt-install build-essential gettext libxslt1.1 libxml2 libxml2-dev libxslt1-dev

COPY requirements.txt /app/
RUN pip install --require-hashes --no-cache-dir -r requirements.txt

COPY . /app
RUN DEBUG=False SECRET_KEY=foo ALLOWED_HOSTS=localhost, DATABASE_URL=sqlite:// \
    ./manage.py collectstatic --noinput
# END BUILDER IMAGE

# FINAL IMAGE
FROM python:3.7-slim-stretch

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV DJANGO_SETTINGS_MODULE=nucleus.settings
ENV PATH="/venv/bin:$PATH"
EXPOSE 8000
CMD ["bin/run-prod.sh"]
WORKDIR /app

COPY docker/bin/apt-install /usr/local/bin/
RUN apt-install libxslt1.1 libxml2 postgresql-client

# add non-priviledged user
RUN adduser --uid 1000 --disabled-password --gecos '' --no-create-home webdev

COPY --from=builder /venv /venv
COPY --from=builder /app /app

ARG GIT_SHA=latest
ENV GIT_SHA=${GIT_SHA}

# Change User
RUN chown webdev.webdev -R .
USER webdev
