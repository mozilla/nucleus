# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from rest_framework import serializers

from .models import Country, Note, Release


class HyperlinkedModelSerializerWithPkField(serializers.HyperlinkedModelSerializer):
    def get_default_field_names(self, declared_fields, model_info):
        fields = super().get_default_field_names(declared_fields, model_info)
        fields.append("id")
        return fields


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "name",
            "code",
        ]


class NoteSerializer(HyperlinkedModelSerializerWithPkField):
    relevant_countries = CountrySerializer(
        read_only=True,
        many=True,
    )

    class Meta:
        model = Note
        fields = "__all__"


class ReleaseSerializer(HyperlinkedModelSerializerWithPkField):
    class Meta:
        model = Release
        fields = "__all__"
