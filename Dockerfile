FROM mozmeao/base:python-2.7

EXPOSE 8000
CMD ["./bin/run-prod.sh"]
WORKDIR /app
ENV DJANGO_SETTINGS_MODULE=nucleus.settings

RUN apt-install build-essential libpq-dev postgresql-client python-psycopg2 gettext xmlsec1 libffi-dev libssl-dev

COPY requirements.txt requirements-saml.txt /app/
RUN pip install --require-hashes --no-cache-dir \
                -r requirements.txt \
                -r requirements-saml.txt

COPY . /app
RUN DEBUG=False SECRET_KEY=foo ALLOWED_HOSTS=localhost, DATABASE_URL=sqlite:// ./manage.py collectstatic --noinput

# Change User
RUN chown webdev.webdev -R .
USER webdev
