import shlex
import re
import logging

from django.db.models import Q

from rest_framework.filters import BaseFilterBackend


log = logging.getLogger(__name__)
splitter = re.compile(r'^(.*[^\s]):([^\s].*)?$')

class InvalidSearchQuery(Exception):
    pass


class FilterBackend(BaseFilterBackend):
    """
    This filter backend provides query string based filtering.
    """

    def filter_queryset(self, request, queryset, view):
        """
        Filtering of the query set is done by the FilterClass

        The FilterClass is defined on the view as the `filter_class`
        attribute.
        """
        if not hasattr(view, 'filter_class'):
            return queryset
        filter = view.filter_class()

        return filter.filter_queryset(request, queryset, view)


class BaseFilter(object):
    def filter_queryset(self, request, queryset, view):
        query_params = request.GET.dict().copy()
        log.debug('Query string: `%s`', request.GET.urlencode())

        if 'search' in query_params:
            search_query = query_params.pop('search', '')
            blaat = self.transform_search_query(search_query)
            blaat.update(query_params)
            query_params = blaat

        for allowed_filter in self.get_all_filters():
            if allowed_filter.name in query_params:
                value = query_params.get(allowed_filter.name)
                queryset = allowed_filter.filter(queryset, value)

        search_query = query_params.pop('search', None)

        if search_query:
            queryset = queryset.filter(
                self.get_searchable_filters(search_query,
                                            self.search_fields)
            )

        return queryset

    def transform_search_query(self, query, unassorted_key='search'):
        """
        Convert a search query into a dictionary.

        A search query like this one:
            party: stakker is akker category:"hiha hoi"

        Will be converted to a python dict:
            {
                'category': 'hiha hoi',
                'party': None,
                'search': 'stakker is akker'
            }

        It uses a regular expression to split every token on the `:`
        separator instead of using the string.split() function. This is
        important to distinguish between the following use cases:

            - 'party:'        => {'party': None}
            - 'party:tester'  => {'party': 'tester'}
            - 'party: tester' => {'search': 'party: tester'}

        """
        retval = {}
        unassorted = []

        log.debug('Raw search query: %s', query)

        try:
            raw_parts = shlex.split(query)
        except ValueError as e:
            message = 'Raw search query could not be parsed: %s' % e
            log.warning(message)
            raise InvalidSearchQuery(message)

        for part in raw_parts:
            parts = splitter.split(part)
            if len(parts) == 4:
                retval[parts[1]] = parts[2]
            else:
                unassorted.append(parts[0])

        if unassorted:
            retval[unassorted_key] = ' '.join(unassorted)

        log.debug('Filter queryset: %s', retval)
        return retval

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
        log.debug(qq)
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
        log.debug('Filter queryset: %s == %s',
                  self.__class__.__name__,
                  filter)

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
