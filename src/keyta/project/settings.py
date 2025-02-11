"""
Django settings for KeyTA project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from django.contrib import admin


LOCALAPPDATA = Path(str(os.getenv('LOCALAPPDATA')))
KEYTA_DIR = LOCALAPPDATA / 'KeyTA'
KEYTA_DIR.mkdir(exist_ok=True)


admin.AdminSite.index_title = 'KeyTA'

def has_permission(self, request):
    from django.contrib.auth.models import User
    user = User.objects.first()
    if not user:
        user = User.objects.create_superuser('keyta', '', 'keyta')

    return setattr(request, 'user', user) or True

admin.AdminSite.has_permission = has_permission # type: ignore

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

BASE_URL = 'http://localhost:8000/'

DEBUG = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-oxz(95c8d8gsgeue_i9nfx^)u92(f+bpp+o^@w7##vu=!4j@be'

INTERNAL_IPS = ['127.0.0.1']

# Application definition

ADMIN_APP = [
    'jazzmin'
]

DEFAULT_APPS = [
    'model_clone',  # model_clone must be placed before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.forms',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]


THIRD_PARTY_APPS = [
    'adminsortable2',
    'django_select2',
    'tinymce'
]

KEYTA_APPS = [
    'apps.actions',
    'apps.executions',
    'apps.keywords',
    'apps.libraries',
    'apps.resources',
    'apps.sequences',
    'apps.systems',
    'apps.testcases',
    'apps.variables',
    'apps.windows'
]

INSTALLED_APPS = ADMIN_APP + DEFAULT_APPS + THIRD_PARTY_APPS + KEYTA_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

SQLITE_DB = KEYTA_DIR / 'db.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': SQLITE_DB
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = os.environ.get('KEYTA_LANG', 'en')

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "locale"
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [STATIC_DIR]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Jazzmin: Use modals instead of popups
X_FRAME_OPTIONS = 'SAMEORIGIN'
JAZZMIN_SETTINGS = {
    "changeform_format_overrides": {
        'actions.actionexecution': 'single',
        'actions.robotkeywordcall': 'single',
        'executions.keywordexecution': 'single',
        'executions.keywordexecutionsetup': 'single',
        'executions.setup': 'single',
        'executions.teardown': 'single',
        'executions.testcaseexecution': 'single',
        'keywords.executionkeywordcall': 'single',
        'libraries.libraryimport': 'single',
        'sequences.actioncall': 'single',
        'sequences.sequenceexecution': 'single',
        'testcases.sequencecall': 'single',
        'keywords.teststep': 'single',
    },
    "copyright": 'imbus',
    "custom_css": "css/keyta.css",
    "hide_models": [
        'auth.group',
        'auth.user',
        'actions.actiondocumentation',
        'actions.actionexecution',
        'actions.actionwindow',
        'actions.actionlibraryimport',
        'actions.robotkeywordcall',
        'actions.windowaction',
        'executions.execution',
        'executions.keywordexecution',
        'executions.testcaseexecution',
        'executions.executionlibraryimport',
        'executions.setup',
        'executions.teardown',
        'executions.keywordexecutionsetup',
        'executions.testcaseexecutionsetupteardown',
        'keywords.executionkeywordcall',
        'keywords.keyword',
        'keywords.keywordcall',
        'keywords.keyworddocumentation',
        'keywords.windowkeywordparameter',
        'keywords.windowkeywordreturnvalue',
        'libraries.librarykeyword',
        'libraries.librarykeyworddocumentation',
        'libraries.libraryimport',
        'libraries.libraryparameter',
        'libraries.libraryinitdocumentation',
        'resources.resourcekeyword',
        'resources.resourcekeyworddocumentation',
        'sequences.sequencedocumentation',
        'sequences.actioncall',
        'sequences.sequenceexecution',
        'sequences.sequenceresourceimport',
        'sequences.windowsequence',
        'keywords.teststep',
        'testcases.testcaseexecution',
        'variables.variablevalue',
        'variables.variablewindow',
        'variables.windowvariable',
        'windows.systemwindow',
        'windows.windowdocumentation',
        'windows.windowlibrary'
    ],
    "icons": {
        "actions.action": "fa-solid fa-cubes-stacked",
        "libraries.library": "fa-solid fa-robot",
        "resources.resource": "fa-solid fa-key",
        "sequences.sequence": "fa-solid fa-arrows-turn-to-dots",
        "systems.system": "fa-solid fa-shapes",
        "testcases.testcase": "fa-solid fa-list-check",
        "variables.variable": "fa-solid fa-arrow-up-right-from-square",
        "windows.window": "fa-solid fa-layer-group"
    },
    "index_title": "KeyTA",
    "order_with_respect_to": [
        'libraries',
        'resources',
        'actions',
        'sequences',
        'variables',
        'testcases',
        'systems',
        'windows',
    ],
    "related_modal_active": True,
    "site_logo": "img/keyta.png",
    "site_brand": "KeyTA",
    "site_header": "KeyTA",
    "site_title": "KeyTA",
    "use_google_fonts_cdn": False,
}

TINYMCE_DEFAULT_CONFIG= {
    "height": "700px",
    "setup": """function (editor) {
        editor.on('blur', function (e) {
        const url = document.URL
        if (url.includes("/change")) {
            editor.save()
            $.post(url, $('form').serialize() + "&_continue=")
        }
    });}"""
}
