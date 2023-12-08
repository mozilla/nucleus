"""
Django settings for nucleus project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import platform
from datetime import timedelta
from os.path import abspath
from pathlib import Path

import dj_database_url
import django_cache_url
import sentry_sdk
import spinach
from decouple import Csv, config
from redis import StrictRedis
from sentry_processor import DesensitizationProcessor
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger
from spinach.contrib.sentry_sdk_spinach import SpinachIntegration

ROOT_PATH = Path(__file__).resolve().parents[1]
GIT_REPOS_PATH = ROOT_PATH / "git-repos"
ROOT = str(ROOT_PATH)


def path(*args):
    return abspath(str(ROOT_PATH.joinpath(*args)))


def git_repo_path(*args):
    return abspath(str(GIT_REPOS_PATH.joinpath(*args)))


WHITENOISE_ROOT = path("root_files")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
ALLOWED_CIDR_NETS = config("ALLOWED_CIDR_NETS", default="", cast=Csv())

ENGAGE_ROBOTS = config("ENGAGE_ROBOTS", cast=bool, default="nucleus.mozilla.org" in ALLOWED_HOSTS)

# Application definition

INSTALLED_APPS = [
    # Project specific apps
    "nucleus.base",
    "nucleus.rna",
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # Third party apps
    "spinach.contrib.spinachd",
    "mozilla_django_oidc",
    "django_jinja",
    "django_extensions",
    "pagedown.apps.PagedownConfig",
    "rest_framework",
    "rest_framework.authtoken",
    "watchman",
]

for app in config("EXTRA_APPS", default="", cast=Csv()):
    INSTALLED_APPS.append(app)

MIDDLEWARE = (
    "allow_cidr.middleware.AllowCIDRMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "nucleus.base.middleware.HostnameMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "nucleus.rna.middleware.PatchOverrideMiddleware",
    "crum.CurrentRequestUserMiddleware",
)

ROOT_URLCONF = "nucleus.urls"

WSGI_APPLICATION = "nucleus.wsgi.application"

# legacy setting
DISABLE_SSL = config("DISABLE_SSL", default=DEBUG, cast=bool)
# SecurityMiddleware settings
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default="0", cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_BROWSER_XSS_FILTER = config("SECURE_BROWSER_XSS_FILTER", default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config("SECURE_CONTENT_TYPE_NOSNIFF", default=True, cast=bool)
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=not DISABLE_SSL, cast=bool)
SECURE_REDIRECT_EXEMPT = [
    r"^healthz/$",
    r"^readiness/$",
]
if config("USE_SECURE_PROXY_HEADER", default=SECURE_SSL_REDIRECT, cast=bool):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# watchman
WATCHMAN_DISABLE_APM = True
WATCHMAN_CHECKS = (
    "watchman.checks.caches",
    "watchman.checks.databases",
)

DATABASES = {"default": config("DATABASE_URL", cast=dj_database_url.parse)}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

CACHES = {
    "default": config("CACHE_URL", default="locmem://", cast=django_cache_url.parse),
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us")

TIME_ZONE = config("TIME_ZONE", default="UTC")

USE_I18N = config("USE_I18N", default=True, cast=bool)

USE_L10N = config("USE_L10N", default=True, cast=bool)

USE_TZ = config("USE_TZ", default=True, cast=bool)

STATIC_ROOT = config("STATIC_ROOT", default=path("static"))
STATIC_URL = config("STATIC_URL", "/static/")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_ROOT = config("MEDIA_ROOT", default=path("media"))
MEDIA_URL = config("MEDIA_URL", "/media/")

SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE

RNA = {"BASE_URL": config("RNA_BASE_URL", default="https://nucleus.mozilla.org/rna/")}
RNA_JSON_CACHE_TIME = config("RNA_JSON_CACHE_TIME", default="600", cast=int)

GITHUB_PUSH_ENABLE = config("GITHUB_PUSH_ENABLE", default="false", cast=bool)
GITHUB_ACCESS_TOKEN = config("GITHUB_ACCESS_TOKEN", default="")
GITHUB_OUTPUT_REPO = config("GITHUB_OUTPUT_REPO", default="mozmeao/nucleus-data")
GITHUB_OUTPUT_BRANCH = config("GITHUB_OUTPUT_BRANCH", default="master")

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "app_dirname": "jinja",
            "match_extension": "",
            "newstyle_gettext": True,
            "context_processors": [
                "nucleus.base.context_processors.settings",
                "nucleus.base.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "nucleus.base.context_processors.settings",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    "DEFAULT_MODEL_SERIALIZER_CLASS": "nucleus.rna.serializers.HyperlinkedModelSerializerWithPkField",
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.DjangoModelPermissions",),
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
}

# Django-CSP
CSP_DEFAULT_SRC = ("'self'",)
CSP_FONT_SRC = (
    "'self'",
    "http://*.mozilla.net",
    "https://*.mozilla.net",
    "http://*.mozilla.org",
    "https://*.mozilla.org",
)
CSP_IMG_SRC = (
    "'self'",
    "http://*.mozilla.net",
    "https://*.mozilla.net",
    "http://*.mozilla.org",
    "https://*.mozilla.org",
)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "http://*.mozilla.org",
    "https://*.mozilla.org",
    "http://*.mozilla.net",
    "https://*.mozilla.net",
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "http://*.mozilla.org",
    "https://*.mozilla.org",
    "http://*.mozilla.net",
    "https://*.mozilla.net",
)

HOSTNAME = platform.node()
K8S_NAMESPACE = config("K8S_NAMESPACE", default=None)
K8S_POD_NAME = config("K8S_POD_NAME", default=None)
CLUSTER_NAME = config("CLUSTER_NAME", default=None)
USE_X_FORWARDED_HOST = True

# Data scrubbing before Sentry
# https://github.com/laiyongtao/sentry-processor
SENSITIVE_FIELDS_TO_MASK_ENTIRELY = [
    # Add custom fieldnames here, to supplement the default keys set at
    # https://github.com/laiyongtao/sentry-processor/blob/master/sentry_processor/sentry_event_processor.py#L13
]
SENSITIVE_FIELDS_TO_MASK_PARTIALLY = [
    # Add custom fieldnames here
]


def before_send(event, hint):
    processor = DesensitizationProcessor(
        with_default_keys=True,
        # Enable the following if required:
        # sensitive_keys=SENSITIVE_FIELDS_TO_MASK_ENTIRELY,
        # Enable the following if required:
        # partial_keys=SENSITIVE_FIELDS_TO_MASK_PARTIALLY,
        # mask_position=POSITION.LEFT,  # from sentry_processor import POSITION (when you need it)
        # off_set=3,
    )
    event = processor.process(event, hint)
    return event


sentry_sdk.init(
    dsn=config("SENTRY_DSN", None),
    release=config("GIT_SHA", None),
    server_name=".".join(x for x in [K8S_NAMESPACE, CLUSTER_NAME, HOSTNAME] if x),
    integrations=[
        SpinachIntegration(send_retries=True),
        DjangoIntegration(),
    ],
    before_send=before_send,
)

REDIS_URL = config("REDIS_URL", None)

SPINACH_NAMESPACE = K8S_NAMESPACE or "nucleus-dev"
SPINACH_CLEAR_SESSIONS_PERIODICITY = timedelta(days=1)
if REDIS_URL:
    SPINACH_BROKER = spinach.RedisBroker(StrictRedis.from_url(REDIS_URL))
else:
    SPINACH_BROKER = spinach.MemoryBroker()

LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": os.getenv("DJANGO_LOG_LEVEL", LOG_LEVEL),
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
        "nucleus": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", LOG_LEVEL),
        },
        "spinach": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", LOG_LEVEL),
        },
        "root": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", LOG_LEVEL),
        },
    },
}

# DisallowedHost gets a lot of action thanks to scans/bots/scripts,
# but we need not take any action because it's already HTTP 400-ed.
# Note that we ignore at the Sentry client level
ignore_logger("django.security.DisallowedHost")

OIDC_ENABLE = config("OIDC_ENABLE", default=False, cast=bool)
if OIDC_ENABLE:
    AUTHENTICATION_BACKENDS = ("nucleus.base.authentication.OIDCModelBackend",)
    OIDC_OP_AUTHORIZATION_ENDPOINT = config("OIDC_OP_AUTHORIZATION_ENDPOINT")
    OIDC_OP_TOKEN_ENDPOINT = config("OIDC_OP_TOKEN_ENDPOINT")
    OIDC_OP_USER_ENDPOINT = config("OIDC_OP_USER_ENDPOINT")

    OIDC_RP_CLIENT_ID = config("OIDC_RP_CLIENT_ID")
    OIDC_RP_CLIENT_SECRET = config("OIDC_RP_CLIENT_SECRET")
    OIDC_CREATE_USER = config("OIDC_CREATE_USER", default=False, cast=bool)
    MIDDLEWARE = MIDDLEWARE + ("mozilla_django_oidc.middleware.SessionRefresh",)
    LOGIN_REDIRECT_URL = "/admin/"
