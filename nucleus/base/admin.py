# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib import admin

from .models import GithubLog
from .tasks import tasks


class GithubLogAdmin(admin.ModelAdmin):
    list_display = ("created", "content_object", "author", "branch", "fail_count", "ack")
    list_filter = ("author", "content_type", "branch", "fail_count", "ack")
    actions = ["requeue"]
    date_hierarchy = "created"

    def requeue(self, request, queryset):
        for ghl in queryset:
            tasks.schedule("nucleus:save_to_github", ghl.pk)

    requeue.short_description = "Run Task Again"


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("action_time", "user", "__str__")
    list_filter = ("user", "content_type")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(GithubLog, GithubLogAdmin)
admin.site.register(admin.models.LogEntry, LogEntryAdmin)
