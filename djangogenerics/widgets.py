from django.utils.safestring import mark_safe
from urllib import urlencode

class DateDrillDownWidget(object):

    def __init__(self, *args, **kwargs):
        self.type = kwargs.get('type', None)
        self.field = kwargs.get('field', None)
        self.dates = kwargs.get('dates', [])
        self.querydict = kwargs.get('querydict', {})

        if not self.field:
            raise ValueError('You must provide DateDrillDownWidget.field')

    def get_query_string_for(self, value):
        data = self.querydict.copy()
        key = '{}__{}'.format(self.field, self.type)
        data[key] = value
        return data

    def get_link(self, date):
        date_value = getattr(date, self.type)
        data = self.get_query_string_for(date_value)
        url = urlencode(data)
        return '<a href="?{}">{}</a>'.format(url, date_value)

    def render(self):
        dates = ['<li>{}</li>'.format(self.get_link(date)) for date in self.dates]
        return mark_safe("\n".join(dates))

    def __str__(self):
        return self.render()

