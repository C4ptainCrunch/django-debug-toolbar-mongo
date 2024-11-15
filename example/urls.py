import views
from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path

urlpatterns = [
    path("", views.index),
    *debug_toolbar_urls(),
]
