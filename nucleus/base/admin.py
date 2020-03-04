# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib import admin


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', '__str__')
    list_filter = ('user', 'content_type')


admin.site.register(admin.models.LogEntry, LogEntryAdmin)
