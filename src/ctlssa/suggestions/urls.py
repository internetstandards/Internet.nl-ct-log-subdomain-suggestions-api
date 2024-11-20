from django.urls import path

from . import views

urlpatterns = [
    path("", views.suggest, name="suggest"),
    # make available under alternative path for when reverse proxied under prefix
    path("ctlssa", views.suggest, name="suggest"),
]
