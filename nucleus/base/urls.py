from django.conf.urls import url
from django.views.generic import TemplateView

from nucleus.base import views

urlpatterns = (
    url(r'^/?$', TemplateView.as_view(template_name='base/home.html'), name='base.home'),
    url('^healthz/$', views.liveness, name='base.liveness'),
    url('^readiness/$', views.readiness, name='base.readiness'),
)
