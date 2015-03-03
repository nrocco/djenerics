from django.core.exceptions import ImproperlyConfigured


class SelectRelatable(object):
    """
    Mixin allows you to provide a tuple or list of related models to
    perform a select_related on.
    """
    select_related = None

    def get_queryset(self):
        if self.select_related is None:
            raise ImproperlyConfigured(
                "%s is missing the "
                "select_related property. This must be a tuple or list." %
                self.__class__.__name__
            )

        if not isinstance(self.select_related, (tuple, list)):
            raise ImproperlyConfigured(
                "%s's select_related property "
                "must be a tuple or list." % self.__class__.__name__
            )

        queryset = super(SelectRelatable, self).get_queryset()

        return queryset.select_related(*self.select_related)
