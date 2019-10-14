Nucleus
=======

The publication platform for Mozilla's marketing websites.

Docker for development
----------------------

Make sure you have [docker](https://www.docker.com/products/docker-desktop) and 
[docker-compose](https://github.com/docker/compose). After those are setup and running
you can use the following commands:

```bash
$ # This file must exist and you can customize environment variables for local dev in it
$ touch .env
$ # this pulls our latest builds from the docker hub.
$ # it's optional but will speed up your builds considerably.
$ docker-compose pull
$ # get the site up and running
$ docker-compose up web
```

If you've made changes to the `Dockerfile` or the `requirements/*.txt` files you'll need to rebuild
the image to run the app and tests:

```bash
$ docker-compose build web
```

Then to run the app you run the `docker-compose up web` command again, or for running tests against your local changes you run:

```bash
$ docker-compose run --rm test
```

We use pytest for running tests. So if you'd like to craft your own pytest command to run individual test files or something
you can do so by passing in a command to the above:

```bash
$ docker-compose run --rm test py.test nucleus/base/tests.py
```

And if you need to debug a running container, you can open another terminal to your nucleus code and run the following:

```bash
$ docker-compose exec web bash
$ # or
$ docker-compose exec web python manage.py shell
```

Managing Python dependencies
----------------------------

For Python we use [pip-compile-multi](https://pypi.org/project/pip-compile-multi/) to manage dependencies expressed in our requirements
files. `pip-compile-multi` is wrapped up in Makefile commands, to ensure we use it consistently.

If you add a new Python dependency (e.g. to `requirements/prod.in` or `requirements/dev.in`) you can generate a pinned and hash-marked
addition to our requirements files by running:

```bash
    make compile-requirements
```

and committing any changes that are made. Please re-build your docker image and test it with `make build test` to be sure the dependency
does not cause a regression.

Similarly, if you *upgrade* a pinned dependency in an `*.in` file, run `make compile-requirements` then rebuild, test and commit the results.

To check for stale Python dependencies (basically `pip list -o` but in the Docker container):

```bash
    make check-requirements
```

Docker for deploying to production
-----------------------------------

1. Add your project in [Docker Registry](https://registry.hub.docker.com/) as [Automated Build](http://docs.docker.com/docker-hub/builds/)
2. Prepare a 'env' file with all the variables needed by dev, stage or production.
3. Run the image:

```bash
$ docker run --env-file env -p 80:8000 mozilla/nucleus
```

Heroku
------
1. heroku create
2. heroku config:set DEBUG=False ALLOWED_HOSTS=<foobar>.herokuapp.com, SECRET_KEY=something_secret
   DATABASE_URL gets populated by heroku once you setup a database.
3. git push heroku master


NewRelic Monitoring
-------------------

A newrelic.ini file is already included. To enable NewRelic monitoring
add two environment variables:

 - NEW_RELIC_LICENSE_KEY
 - NEW_RELIC_APP_NAME

See the [full list of supported environment variables](https://docs.newrelic.com/docs/agents/python-agent/installation-configuration/python-agent-configuration#environment-variables).


## Kubernetes

https://github.com/mozmeao/nucleus-config/ has public examples of deployments in k8s clusters in AWS & GCP.


## Gitlab CI/CD

We have https://gitlab.com/mozmeao/nucleus/pipelines [set up as CI/CD for](https://gitlab.com/mozmeao/infra/blob/master/docs/gitlab_ci.md)  https://github.com/mozilla/nucleus via this [.gitlab-ci.yml](https://github.com/mozilla/nucleus/blob/gitlab/.gitlab-ci.yml), which [updates the config repo](https://github.com/mozilla/nucleus/blob/gitlab/bin/update-config.sh) triggering https://gitlab.com/mozmeao/nucleus/pipelines configured by [.gitlab-ci.yml in the config repo](https://github.com/mozilla/nucleus-config/blob/master/.gitlab-ci.yml).
