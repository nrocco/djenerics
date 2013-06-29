from django.core.urlresolvers import reverse
from django.forms import CharField
from django.forms import ValidationError
from django.forms.fields import CharField
from django.forms.util import flatatt
from django.forms.widgets import DateInput as DjangoDateInput
from django.forms.widgets import DateTimeInput as DjangoDateTimeInput
from django.forms.widgets import TextInput
from django.forms.widgets import TimeInput as DjangoTimeInput
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe



class EmailInput(TextInput):
    input_type = 'email'


class NumberInput(TextInput):
    input_type = 'number'


class TelephoneInput(TextInput):
    input_type = 'tel'


class DateInput(DjangoDateInput):
    input_type = 'date'


class DateTimeInput(DjangoDateTimeInput):
    input_type = 'datetime'


class TimeInput(DjangoTimeInput):
    input_type = 'time'


class ForeignKeyAutoCompleteField(CharField):

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model", False)
        widget = kwargs.get("widget", False)

        if not widget or not isinstance(widget, ForeignKeyAutoCompleteWidget):
            kwargs["widget"] = ForeignKeyAutoCompleteWidget(
                model = self.model,
                datakey = kwargs.pop("datakey", 'name'),
                datalist = kwargs.pop('datalist', ''),
                endpoint = kwargs.pop("endpoint", '')
            )

        super(ForeignKeyAutoCompleteField, self).__init__(max_length=255, *args, **kwargs)

    def clean(self, value):
        if value:
            return self.model.objects.get(pk=value)
        else:
            if self.required:
                raise ValidationError(self.error_messages['required'])
            return None



class ForeignKeyAutoCompleteWidget(TextInput):

    class Media:
        js = (
            'djangogenerics/js/ForeignKeyAutoCompleteWidget.js',
        )

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model", False)
        self.datakey = kwargs.pop("datakey", False)
        self.datalist = kwargs.pop('datalist', False)
        self.endpoint = kwargs.pop("endpoint", False)
        super(ForeignKeyAutoCompleteWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        value = value or ''

        hidden_attrs = {
            'id': attrs.pop('id'),
            'name': name
        }

        attrs['class'] = 'djangojax-fkac'
        attrs['data-store'] = hidden_attrs['id']
        attrs['data-remote'] = self.endpoint
        attrs['data-key'] = self.datakey

        if self.datalist:
            attrs['data-list'] = self.datalist

        if value:
            try:
                obj = self.model.objects.get(pk=value)
            except:
                raise Exception("Cannot find %s object with primary key: %s" % (name, value))
            attrs["value"] = getattr(obj, self.datakey)
            hidden_attrs["value"] = value

        return mark_safe(u'<input type="hidden"%s /><input type="text"%s/>' % (flatatt(hidden_attrs), flatatt(attrs)))
