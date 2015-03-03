from rest_framework.pagination import BasePaginationSerializer
from rest_framework.pagination import NextPageField
from rest_framework.pagination import PreviousPageField
from rest_framework.serializers import Serializer
from rest_framework.serializers import ReadOnlyField


class CurrentPageField(ReadOnlyField):
    """
    Field that returns a link to the current page in paginated results.
    """
    def to_native(self, value):
        return value.number


class NextPageField(ReadOnlyField):
    """
    Field that returns a link to the next page in paginated results.
    """
    def to_native(self, value):
        if not value.has_next():
            return None
        return value.next_page_number()


class PreviousPageField(ReadOnlyField):
    """
    Field that returns a link to the previous page in paginated results.
    """
    def to_native(self, value):
        if not value.has_previous():
            return None
        return value.previous_page_number()


class PagesSerializer(Serializer):
    current = CurrentPageField(source='*')
    next = NextPageField(source='*')
    prev = PreviousPageField(source='*')
    # total = ReadOnlyField(source='_num_pages')


class PaginationSerializer(BasePaginationSerializer):
    """
    A default implementation of a pagination serializer.
    """
    total = ReadOnlyField(source='paginator.count')
    limit = ReadOnlyField(source='paginator.per_page')
    # pages = PagesSerializer(source='*')
