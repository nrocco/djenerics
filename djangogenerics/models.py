from django.db import models

class Timestampable(models.Model):
    '''
        add comments to these classes
    '''
    created = models.DateTimeField(auto_now_add=True,editable=False)
    updated = models.DateTimeField(auto_now=True,editable=False)

    class Meta:
        abstract = True

class TimestampableModelMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True,editable=False)
    updated = models.DateTimeField(auto_now=True,editable=False)

    class Meta:
        abstract = True
