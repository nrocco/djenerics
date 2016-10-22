import shlex
import re
from django.conf import settings
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

DEFAULT_SEARCH_PARAM = 'search'

class FilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not hasattr(view, 'filter_class'):
            return queryset
        filter = view.filter_class()

        return filter.filter_queryset(request, queryset, view)


class BaseFilter(object):
    def filter_queryset(self, request, queryset, view):
        for allowed_filter in self.get_all_filters():
            if allowed_filter.name in request.GET:
                value = request.GET[allowed_filter.name]
                queryset = allowed_filter.filter(queryset, value)

        key = settings.REST_FRAMEWORK.get('SEARCH_PARAM',
                                          DEFAULT_SEARCH_PARAM)

        if key in request.GET:
            queryset = queryset.filter(
                self.get_searchable_filters(request.GET[key],
                                            self.search_fields)
            )

        return queryset

    def get_all_filters(self):
        filters = []
        for attr in dir(self):
            if not attr.startswith('__'):
                filter = getattr(self, attr)
                if isinstance(filter, FilterField):
                    filter.name = attr
                    filters.append(filter)
        return filters

    def get_searchable_filters(self, query, search_fields):
        parts = shlex.split(query)
        qq = Q()
        for field in search_fields:
            filter = '%s__icontains' % field
            q = Q()
            for part in parts:
                q &= Q(**{filter: part})
            qq |= q
        return qq


class FilterField(object):
    model_field = None
    lookup_type = 'exact'

    def __init__(self, model_field=None, **kwargs):
        self.model_field = model_field
        if 'lookup_type' in kwargs:
            self.lookup_type = kwargs['lookup_type']

    def clean(self, value):
        return value

    def get_key(self):
        field = self.model_field or self.name

        if self.lookup_type:
            key = field + '__' + self.lookup_type
        else:
            key = field
        return key

    def filter(self, queryset, value):
        self.raw_value = value
        filter = {self.get_key(): self.clean(value)}
        return queryset.filter(**filter)


class CharFilterField(FilterField):
    def clean(self, value):
        return value or ''


class NumberFilterField(FilterField):
    lookup_type = None

    def get_key(self):
        if not self.raw_value:
            return '%s__isnull' % (self.model_field or self.name)
        else:
            return super(NumberFilterField, self).get_key()

    def clean(self, value):
        if not value:
            return True
        return int(value)


class FloatFilterField(NumberFilterField):
    blaat = re.compile(r'\.(?=[^.]*\.)')

    def clean(self, value):
        if not value:
            return True

        value = value.replace(',', '.')
        clean_value = self.blaat.sub('', value)

        return float(clean_value)


class RelatedFilterField(FilterField):
    related_name = 'slug'
    lookup_type = 'icontains'

    def __init__(self, model_field=None, **kwargs):
        super(RelatedFilterField, self).__init__(model_field, **kwargs)
        if 'related_name' in kwargs:
            self.related_name = kwargs['related_name']

    def get_key(self):
        if not self.raw_value:
            key = '%s__isnull' % (self.model_field or self.name)
        else:
            key = '%s__%s__%s' % ((self.model_field or self.name),
                                  self.related_name,
                                  self.lookup_type)
        return key

    def clean(self, value):
        return value or True


class BooleanFilterField(FilterField):
    def clean(self, value):
        if value == 'True' or value == '1' or value == 'true':
            return True
        elif value == 'False' or value == '0' or value == 'false':
            return False
        return bool(value)
