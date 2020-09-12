from django.urls import path

from .views import *

urlpatterns = [
    path("get_register_code", get_register_code),
    path("register", register),
    path("login", login),
    path("logout", logout),
    path("retrieve", retrieve),
]