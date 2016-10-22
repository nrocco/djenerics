from django.conf import settings

DEFAULT_PROJECTION_PARAM = '_fields'

class Ownerable(object):
    def __init__(self, *args, **kwargs):
        '''
        Temporary workaround for:
          - https://github.com/tomchristie/django-rest-framework/issues/1811
          - https://github.com/tomchristie/django-rest-framework/issues/2292
        '''
        user = kwargs['context']['request'].user

        for field_name in self.Meta.ownerable_fields:
            field = self.fields[field_name]
            field.queryset = field.queryset.filter(owner=user)

        super(Ownerable, self).__init__(*args, **kwargs)


class Projectable(object):
    def __init__(self, *args, **kwargs):
        if 'context' in kwargs and 'request' in kwargs['context']:
            request = kwargs['context']['request']
            key = settings.REST_FRAMEWORK.get('PROJECTION_PARAM',
                                              DEFAULT_PROJECTION_PARAM)

            if key in request.GET and request.GET[key]:
                preferred_fields = set(request.GET[key].split(','))
                for field in set(self.fields.keys()):
                    if field not in preferred_fields:
                        self.fields.pop(field)

        super(Projectable, self).__init__(*args, **kwargs)
