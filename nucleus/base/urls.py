from django.conf.urls import url

from nucleus.base import views


urlpatterns = (
    url(r'^/?$', views.home, name='base.home'),
)
