# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from pagedown.widgets import AdminPagedownWidget

from . import models

pagedown_widget_help_text = mark_safe(
    "<span class='img-attr-note'>If you use an <code>&lt;img&gt;</code> tag, any <code>alt</code> "
    "attribute must the last in the tag, else the image "
    "<a target='_blank' href='https://github.com/StackExchange/pagedown/issues/105'>will not preview</a></span>"
)


class NoteAdminForm(forms.ModelForm):
    note = forms.CharField(
        widget=AdminPagedownWidget(),
        help_text=pagedown_widget_help_text,
    )
    bug = forms.IntegerField(
        widget=forms.NumberInput(attrs={"style": "width: 12em;"}),
        required=False,
    )

    class Meta:
        model = models.Note
        fields = "__all__"  # noqa: DJ007


class NoteAdmin(admin.ModelAdmin):
    form = NoteAdminForm
    filter_horizontal = ["releases", "relevant_countries"]
    list_display = ("id", "bug", "tag", "note", "created")
    list_display_links = ("id",)
    list_filter = ("tag", "is_known_issue", "releases__product", "releases__version", "progressive_rollout")
    search_fields = ("bug", "note", "releases__version")


class ReleaseAdminForm(forms.ModelForm):
    system_requirements = forms.CharField(
        widget=AdminPagedownWidget(),
        required=False,
        help_text=pagedown_widget_help_text,
    )
    text = forms.CharField(
        widget=AdminPagedownWidget(),
        required=False,
        help_text=pagedown_widget_help_text,
    )
    release_date = forms.DateTimeField(widget=admin.widgets.AdminDateWidget)

    class Meta:
        model = models.Release
        fields = (
            "is_public",
            "product",
            "channel",
            "version",
            "release_date",
            "text",
            "bug_list",
            "bug_search_url",
            "system_requirements",
            "reviewed_by_release_manager",
        )


class ReleaseAdmin(admin.ModelAdmin):
    actions = ["copy_releases", "set_to_public", "set_to_private"]
    form = ReleaseAdminForm
    list_display = ("version", "product", "channel", "is_public", "release_date", "text", "url")
    list_filter = ("product", "channel", "is_public")
    ordering = ("-release_date",)
    search_fields = ("version", "text")

    class Media:
        js = ["js/release-notes.js"]

    def url(self, obj):
        base_url_staging = "https://www-dev.allizom.org/en-US"
        base_url_prod = "https://www.mozilla.com/en-US"
        product = ""

        if obj.product == "Firefox for Android":
            product = "firefox/android"
        if obj.product == "Firefox for iOS":
            product = "firefox/ios"
        elif obj.product == "Firefox" or obj.product == "Firefox Extended Support Release":
            product = "firefox"
        elif obj.product == "Thunderbird":
            product = "thunderbird"
        elif obj.product == "Firefox OS":
            # Special case for Firefox OS. URL are different
            return format_html(
                '<a href="{staging}/firefox/os/notes/{version}/">Staging</a> / <a href="{prod}/firefox/os/notes/{version}/">Public</a>',
                staging=base_url_staging,
                product=product,
                version=obj.version,
                prod=base_url_prod,
            )

        return format_html(
            '<a href="{staging}/{product}/{version}/releasenotes/">Staging</a> / <a href="{prod}/{product}/{version}/releasenotes/">Public</a>',
            staging=base_url_staging,
            product=product,
            version=obj.version,
            prod=base_url_prod,
        )

    def copy_releases(self, request, queryset):
        release_count = 0
        for release in queryset:
            release_count += 1
            copy_count = self.model.objects.filter(version__endswith=release.version, product=release.product).count()
            notes = list(release.note_set.all())
            copy = release
            copy.id = None
            if copy_count > 1:
                copy.version = f"copy{copy_count}-{copy.version}"
            else:
                copy.version = "copy-" + copy.version
            # By default, set it to public. Usually, the copy feature is
            # used when copying beta => release. We want to review it
            # before going live.
            copy.is_public = False
            copy.save()
            copy.note_set.add(*notes)
            copy.note_set.update(modified=now())
        if release_count == 1:
            self.message_user(request, "Copied Release")
        else:
            self.message_user(request, "Copied %s Releases" % release_count)

    def set_to_public(self, request, queryset):
        """Set one or several releases to public"""
        # save them individually so that signals are sent
        for obj in queryset:
            obj.is_public = True
            obj.save()

    def set_to_private(self, request, queryset):
        """Set one or several releases to private"""
        # save them individually so that signals are sent
        for obj in queryset:
            obj.is_public = False
            obj.save()


class CountryAdmin(admin.ModelAdmin):
    search_fields = ("name", "code")

    class Meta:
        model = models.Country


admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.Note, NoteAdmin)
admin.site.register(models.Release, ReleaseAdmin)
