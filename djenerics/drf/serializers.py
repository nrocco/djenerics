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
        try:
            projection_param = self.Meta.projection_param
        except AttributeError:
            projection_param = '_fields'

        fields = kwargs['context']['request'].GET.get(projection_param)

        if fields:
            allowed = set(fields.split(','))
            existing = set(self.fields.keys())

            for field_name in existing - allowed:
                self.fields.pop(field_name)

        super(Projectable, self).__init__(*args, **kwargs)
