from django.contrib import admin
from django.db import models

from mock import Mock, patch

from django_browserid.admin import BrowserIDAdminSite
from django_browserid.tests import TestCase


class BrowserIDAdminSiteTests(TestCase):
    def test_copy_registry(self):
        # copy_registry should register the ModelAdmins from the given
        # site on the BrowserIDAdminSite.
        django_site = admin.AdminSite()
        browserid_site = BrowserIDAdminSite()

        class TestModel(models.Model):
            pass
        class TestModelAdmin(admin.ModelAdmin):
            pass

        browserid_site.register = Mock()
        django_site.register(TestModel, TestModelAdmin)

        browserid_site.copy_registry(django_site)
        browserid_site.register.assert_any_call(TestModel, TestModelAdmin)

    def test_copy_registry_multiple(self):
        django_site = admin.AdminSite()
        browserid_site = BrowserIDAdminSite()

        class TestModel(models.Model):
            pass
        class TestModel2(models.Model):
            pass
        class TestModel3(models.Model):
            pass
        class TestModelAdmin(admin.ModelAdmin):
            pass
        class TestModel2Admin(admin.ModelAdmin):
            pass

        browserid_site.register = Mock()
        django_site.register(TestModel, TestModelAdmin)
        django_site.register(TestModel2, TestModel2Admin)
        django_site.register(TestModel3, TestModelAdmin)

        browserid_site.copy_registry(django_site)
        browserid_site.register.assert_any_call(TestModel, TestModelAdmin)
        browserid_site.register.assert_any_call(TestModel2, TestModel2Admin)
        browserid_site.register.assert_any_call(TestModel3, TestModelAdmin)

    def test_copy_registry_default_site(self):
        # If no site is given to copy_registry, it should default to
        # django.contrib.admin.site.
        django_site = admin.AdminSite()
        browserid_site = BrowserIDAdminSite()

        class TestModel(models.Model):
            pass
        class TestModelAdmin(admin.ModelAdmin):
            pass

        browserid_site.register = Mock()
        django_site.register(TestModel, TestModelAdmin)

        with patch('django_browserid.admin.admin_site', django_site):
            browserid_site.copy_registry()
        browserid_site.register.assert_any_call(TestModel, TestModelAdmin)
