from django.urls import path

from . import views

urlpatterns = [
    path("", views.suggest, name="suggest"),
]
