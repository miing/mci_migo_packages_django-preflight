import os
import django

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'database.sqlite3',
    }
}

# Old db setup
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'database.sqlite3'

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
MEDIA_ROOT = ''
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'
SECRET_KEY = 'j0-wo!y4zwi)tejv1u(0skc41_379ls^@qbh91%#5o=greje6('

ROOT_URLCONF = 'preflight_example_project.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.realpath(os.path.dirname(__file__)), 'templates'),
)

from django.template.loaders import filesystem
if hasattr(filesystem, 'Loader'):
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
else:
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.load_template_source',
        'django.template.loaders.app_directories.load_template_source',
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'preflight',
    'app',
)

USE_GARGOYLE = django.VERSION[:2] > (1, 1)
if USE_GARGOYLE:
    INSTALLED_APPS = INSTALLED_APPS + ('gargoyle',)

PREFLIGHT_BASE_TEMPLATE = 'base.html'
