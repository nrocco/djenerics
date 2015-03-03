from django.conf import settings
from django.db.models import Model
from django.db.models import DateTimeField
from django.db.models import ForeignKey

class Timestampable(Model):
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Ownerable(Model):
    owner = ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        abstract = True
