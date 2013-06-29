from django.forms import ChoiceField
from django.forms import ModelChoiceField
from django.forms import Form



class Filter(Form):

    # Human-readable title for this filter widget
    title = None

    # Parameter for the filter that will be used in the URL query.
    parameter_name = None

    def __init__(self, *args, **kwargs):
        super(Filter, self).__init__(*args, **kwargs)

        if not self.parameter_name:
            raise ValueError('parameter_name is not set')

        self.fields[self.parameter_name] = self.get_filter_widget()
        self.fields[self.parameter_name].required = False
        self.fields[self.parameter_name].widget.attrs.update(
            {
                'class' : 'simple_choice_filter',
                'onchange': 'simple_choice_filter_changed(this)'
            }
        )
        if self.title:
            self.fields[self.parameter_name].name = self.title

    def get_filter_widget(self):
        raise NotImplementedError('get_filter_widget must be implemented.')

    def value(self):
        """
        Returns the value for this filter from the query string
        """
        if not hasattr(self, 'cleaned_data'):
            self.is_valid()
        return self.cleaned_data.get(self.parameter_name)

    def get_filtered_queryset(self, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(**{self.parameter_name:self.value()})
        else:
            return queryset


class SimpleChoiceFilter(Filter):

    empty_label = 'All'

    class Media:
        js = ('filters/SimpleChoiceFilter.js',)

    def get_filter_options(self):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        raise NotImplementedError('get_filter_options must be implemented')
    
    def get_filter_widget(self):
        return ChoiceField(
            choices=[('', self.empty_label)] + self.get_filter_options()
        )


class ModelChoiceFilter(SimpleChoiceFilter):

    def get_filter_widget(self):
        return ModelChoiceField(
            empty_label=self.empty_label,
            queryset=self.get_filter_options(),
        )

    def get_filter_options(self):
        """
        By default return all the objects for this model
        """
        return self.model.objects.all()



