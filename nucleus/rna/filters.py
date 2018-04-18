# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import django_filters
from django_filters.rest_framework import DjangoFilterBackend

from nucleus.rna import models


class TimestampedFilterBackend(DjangoFilterBackend):
    def get_filter_class(self, view, queryset=None):
        filter_class = getattr(view, 'filter_class', None)
        filter_fields = getattr(view, 'filter_fields', None)
        filter_fields_exclude = getattr(view, 'filter_fields_exclude', ())

        if filter_class or filter_fields:
            return super(TimestampedFilterBackend, self).get_filter_class(
                view, queryset=queryset)

        elif queryset and hasattr(queryset, 'model') and issubclass(
                queryset.model, models.TimeStampedModel):
            class AutoFilterSet(self.default_filter_set):
                created_before = django_filters.IsoDateTimeFilter(
                    name='created', lookup_expr='lt')
                created_after = django_filters.IsoDateTimeFilter(
                    name='created', lookup_expr='gte')

                modified_before = django_filters.IsoDateTimeFilter(
                    name='modified', lookup_expr='lt')
                modified_after = django_filters.IsoDateTimeFilter(
                    name='modified', lookup_expr='gte')

                class Meta:
                    model = queryset.model
                    fields = ['created_before', 'created_after',
                              'modified_before', 'modified_after']
                    fields.extend(f.name for f in model._meta.fields
                                  if f.name not in ('created', 'modified'))
                    fields = [f for f in fields
                              if f not in filter_fields_exclude]
                    order_by = True
            return AutoFilterSet
