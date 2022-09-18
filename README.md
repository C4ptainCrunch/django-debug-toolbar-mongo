
# Django Debug Toolbar MongoDB Panel

## Install

```
poetry add git+https://github.com/CrazyPilot/django-debug-toolbar-mongo.git --group dev
```

## Setup

Add the following lines to your `settings.py`:

```python
   INSTALLED_APPS = (
       ...
       'debug_toolbar_mongo',
       ...
   )

   DEBUG_TOOLBAR_PANELS = (
       ...
       'debug_toolbar_mongo.MongoPanel',
       ...
   )
```

An extra panel titled "MongoDB" should appear in your debug toolbar.