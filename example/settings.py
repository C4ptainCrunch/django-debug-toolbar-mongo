import os

SRC_DIR = os.path.dirname(__file__)

DEBUG = True

ROOT_URLCONF = "urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MONGO_CONN = "mongodb://localhost:27017/?readPreference=primary&ssl=false"
MONGO_DB = "test"
MONGO_COLLECTION = "test"

SECRET_KEY = "bfh00suq6pvqr0hn+9jw37g=^uc3(=pa#eyv&mrus#ao%-v7(e"

MIDDLEWARE = ("debug_toolbar.middleware.DebugToolbarMiddleware",)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    },
]

INSTALLED_APPS = (
    "django.contrib.staticfiles",
    "debug_toolbar",
    "debug_toolbar_mongo",
    "example",
)

STATIC_URL = "static/"

DEBUG_TOOLBAR_PANELS = (
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar_mongo.MongoPanel",
    "debug_toolbar.panels.sql.SQLPanel",
)

INTERNAL_IPS = ("127.0.0.1",)
