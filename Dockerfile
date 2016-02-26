FROM debian:jessie

EXPOSE 8000
CMD ["./bin/run-prod.sh"]

RUN adduser --uid 1000 --disabled-password --gecos '' --no-create-home webdev

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential python python-dev python-pip \
                                               libpq-dev postgresql-client python-psycopg2 gettext && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Get pip 8
COPY bin/pipstrap.py bin/pipstrap.py
RUN bin/pipstrap.py

COPY requirements.txt /app/requirements.txt
RUN pip install --require-hashes --no-cache-dir --ignore-installed -r requirements.txt

COPY . /app
RUN DEBUG=False SECRET_KEY=foo ALLOWED_HOSTS=localhost, DATABASE_URL=sqlite:// ./manage.py collectstatic --noinput -c

# Change User
RUN chown webdev.webdev -R .
USER webdev
