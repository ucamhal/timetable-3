from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns(
    "",

    url(r'administration/help$',
        views.home,
        name="home"),
)
