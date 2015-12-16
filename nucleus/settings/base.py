# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use local.py
import dj_database_url
from funfactory.settings_base import *


# Django Settings
##############################################################################

# Note: be sure not to put any spaces in the env var
ADMINS = [('admin', email) for email in
          os.environ.get('ADMIN_EMAILS', '').split(',')]
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
SERVER_EMAIL= os.environ.get('SERVER_EMAIL', 'root@localhost')

ROOT_URLCONF = 'nucleus.urls'

# Whether the app should run in debug-mode.
DEBUG = os.environ.get('DJANGO_DEBUG', False)

# Configure database from DATABASE_URL environment variable.
DATABASES = {'default': dj_database_url.config()}

# Pull secret keys from environment.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
HMAC_KEYS = {'hmac_key': os.environ.get('DJANGO_HMAC_KEY', '')}

INSTALLED_APPS = [
    # Nucleus and API apps.
    'nucleus.base',
    'rna',

    # Django contrib apps.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # Third-party apps, patches, fixes.
    'south',  # Must come before django_nose.
    'commonware.response.cookies',
    'django_browserid',
    'django_extensions',
    'django_nose',
    'funfactory',
    'pagedown',
    'rest_framework',
    'rest_framework.authtoken',
    'session_csrf',
]

AUTHENTICATION_BACKENDS = [
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'funfactory.context_processors.globals',
    'django_browserid.context_processors.browserid',
)

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'multidb.middleware.PinningRouterMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',  # Must be after auth middleware.
    'django.contrib.messages.middleware.MessageMiddleware',
    'commonware.middleware.FrameOptionsHeader',
)

LOGGING = {
    'loggers': {
        'playdoh': {
            'level': logging.DEBUG
        }
    }
}

USE_TZ = True

# Needed for request.is_secure to work with stackato.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Third-party Libary Settings
##############################################################################

# Testing configuration.
NOSE_ARGS = ['--logging-clear-handlers', '--logging-filter=-south']

# Template paths that contain non-Jinja templates.
JINGO_EXCLUDE_APPS = (
    'admin',
    'registration',
    'rest_framework',
    'rna',
    'browserid',
)

# Always generate a CSRF token for anonymous users.
ANON_ALWAYS = True

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rna.serializers.HyperlinkedModelSerializerWithPkField',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),

    'DEFAULT_FILTER_BACKENDS': ('rna.filters.TimestampedFilterBackend',)
}

# django-browserid -- no spaces allowed in stackato env vars
BROWSERID_AUDIENCES = os.environ.get('BROWSERID_AUDIENCES',
                                     'http://localhost:8000').split(',')


# Nucleus-specific Settings
##############################################################################

# Should robots.txt deny everything or disallow a calculated list of URLs we
# don't want to be crawled?  Default is false, disallow everything.
ENGAGE_ROBOTS = False

# RNA (Release Notes) Configuration
RNA = {
    'BASE_URL': os.environ.get(
        'RNA_BASE_URL', 'https://nucleus.mozilla.org/rna/'),
    'LEGACY_API': os.environ.get('RNA_LEGACY_API', False)
}
