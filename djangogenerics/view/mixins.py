import shlex

from django.db.models import Q
from django.forms import Form
from django.forms import CharField
from django.forms import ChoiceField
from django.forms import HiddenInput

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from djangogenerics.widgets import DateDrillDownWidget

class LoginRequiredMixin(object):
    """
    A login required mixin for use with class based views.
    This Class is a light wrapper around the `login_required` decorator and
    hence function parameters are just attributes defined on the class.

    Due to parent class order traversal this mixin must be added as the
    left most mixin of a view.

    The mixin has exaclty the same flow as `login_required` decorator:

        If the user isn't logged in, redirect to settings.LOGIN_URL,
        passing the current absolute path in the query string.
        Example: /accounts/login/?next=/polls/3/.

        If the user is logged in, execute the view normally.
        The view code is free to assume the user is logged in.

    **Class Settings**
        `redirect_field_name - defaults to "next"
        `login_url` - the login url of your site

    """
    redirect_field_name = REDIRECT_FIELD_NAME
    login_url = None

    @method_decorator(login_required(redirect_field_name=redirect_field_name, login_url=login_url))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)



class InitialDataFormViewMixin(object):

    def get_initial(self):
        initial = super(InitialDataFormViewMixin, self).get_initial()
        if "GET" == self.request.method:
            if self.request.GET:
                for key,value in self.request.GET.items():
                    initial[key] = value
        return initial



class SearchableListMixin(object):

    searchable_fields = []
    searchable_key = 'q'
    searchable_label = 'Search'
    searchable_lookup_type = 'icontains'

    def __init__(self, *args, **kwargs):
        if not isinstance(self.searchable_fields, list):
            raise AssertionError(
                'searchable_fields must be a list'
            )
        if not len(self.searchable_fields) > 0:
            raise AssertionError(
                'searchable_fields cannot be empty'
            )
        super(SearchableListMixin, self).__init__(*args, **kwargs)

    def _create_search_form(self, request):
        form = Form(request.GET)
        form.fields[self.searchable_key] = CharField(
            label = self.searchable_label,
            required = False
        )
        form.fields[self.searchable_key].widget.attrs.update(
           {
               'class': 'searchable-form',
               'placeholder': '...',
           }
        )

        # Add hidden input fields to keep current query sting
        for key, value in request.GET.items():
            if key != self.searchable_key:
                form.fields[key] = CharField(widget=HiddenInput())

        return form

    def dispatch(self, request, *args, **kwargs):
        self.search_form = self._create_search_form(request)
        return super(SearchableListMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchableListMixin, self).get_context_data(**kwargs)
        context['searchable'] = {
            'form': self.search_form,
            'key': self.searchable_key,
            'value': self.request.GET.get(self.searchable_key, '')
        }
        return context

    def get_queryset(self):
        queryset = super(SearchableListMixin, self).get_queryset()
        search_query = self.request.GET.get(self.searchable_key, False)
        if search_query:
            return queryset.filter(
                self.get_searchable_filters(search_query)
            )
        else:
            return queryset

    def get_searchable_filters(self, query):
        parts = shlex.split(query)
        qq = Q()
        for field in self.searchable_fields:
            filter = '%s__%s' % (field, self.searchable_lookup_type)
            q = Q()
            for part in parts:
                q &= Q(**{filter:part})
            qq |= q
        return qq



class FilterableListMixin(object):

    allowed_filters = []
    filter_widgets = []

    def dispatch(self, request, *args, **kwargs):
        """
        Initializes all the filter widgets passing in the request
        """
        self.filter_widgets = [f(request.GET) for f in self.filter_widgets]
        return super(FilterableListMixin, self).dispatch(request, *args, **kwargs)

    def get_filterable_filters(self):
        model_fields = self.model._meta.get_all_field_names()
        filters = {}
        for allowed_filter in self.allowed_filters:
            for get_param in self.request.GET:
                if get_param.startswith(allowed_filter):
                    value = self.request.GET.get(get_param)
                    filters[get_param] = value
        return filters

    def get_context_data(self, **kwargs):
        context = super(FilterableListMixin, self).get_context_data(**kwargs)
        context['filters'] = self.filter_widgets
        return context

    def get_queryset(self):
        queryset = super(FilterableListMixin, self).get_queryset()

        for f in self.filter_widgets:
            queryset = f.get_filtered_queryset(queryset)
        return queryset.filter(**self.get_filterable_filters())




class RedirectRefererMixin(object):
    def form_valid(self, form):
        referer = self.request.POST.get('_referer', None)
        if referer:
            self.success_url = referer
        return super(RedirectRefererMixin, self).form_valid(form)



class MassActionsMixin(object):

    mass_actions = []

    def _create_mass_actions_form(self):
        """
        Creates the actions form and bounds it to the request.POST
        """
        form = Form()
        form.fields['_selected_action'] = ChoiceField(
            label='Actions',
            required = False,
            choices=[('', '---')] + [(a.__name__, a.short_description) for a in self.mass_actions]
        )
        form.fields['_selected_objects'] = CharField(
            required = False,
            widget=HiddenInput()
        )
        return form

    def dispatch(self, request, *args, **kwargs):
        """
        Detect if a mass_action was selected.
        If so, render that output instead of the view itself
        """
        if '_selected_action' in request.POST:
            return self.render_mass_action(request.POST['_selected_action'], request)
        else:
            self.mass_actions_form = self._create_mass_actions_form()
        return super(MassActionsMixin, self).dispatch(request, *args, **kwargs)

    def render_mass_action(self, action, request):
        for mass_action in self.mass_actions:
            if mass_action.__name__ == action and hasattr(mass_action, '__call__'):
                ids = [int(id) for id in request.POST.get('_selected_objects', '').split(',')]
                return mass_action(
                    request,
                    self.model.objects.filter(pk__in=ids)
                )

    def get_context_data(self, **kwargs):
        context = super(MassActionsMixin, self).get_context_data(**kwargs)
        context['actions'] = {
            'form': self.mass_actions_form,
        }
        return context



class SelectRelatedMixin(object):
    """
    Mixin allows you to provide a tuple or list of related models to
    perform a select_related on.
    """
    select_related = None

    def get_queryset(self):
        if self.select_related is None:
            raise ImproperlyConfigured(u"%(cls)s is missing the "
                "select_related property. This must be a tuple or list." % {
                    "cls": self.__class__.__name__})

        if not isinstance(self.select_related, (tuple, list)):
            raise ImproperlyConfigured(u"%(cls)s's select_related property "
                "must be a tuple or list." % {"cls": self.__class__.__name__})

        queryset = super(SelectRelatedMixin, self).get_queryset()
        return queryset.select_related(*self.select_related)



class DateDrillDownMixin(object):

    dd_date_field = None
    dd_date_values = None

    def _get_year_key(self):
        return '{}__year'.format(self.dd_date_field)

    def _get_month_key(self):
        return '{}__month'.format(self.dd_date_field)

    def _get_day_key(self):
        return '{}__day'.format(self.dd_date_field)


    def dispatch(self, request, *args, **kwargs):
        if not self.dd_date_field:
            raise ValueError(u"%(cls)s is missing the "
               "dd_date_field property. This must be set to one "
                "of the model fields" % {'cls':self.__class__.__name__})

        self.dd_date_values = {}

        y_key = self._get_year_key()
        m_key = self._get_month_key()
        d_key = self._get_day_key()

        y_val = request.GET.get(y_key, None)
        m_val = request.GET.get(m_key, None)
        d_val = request.GET.get(d_key, None)

        if y_val:
            self.dd_date_values[y_key] = y_val
        if m_val:
            self.dd_date_values[m_key] = m_val
        if d_val:
            self.dd_date_values[d_key] = d_val

        return super(DateDrillDownMixin, self).dispatch(request, *args, **kwargs)

    def _get_dd_date_type(self):
        if self._get_year_key() in self.dd_date_values and \
           self._get_month_key() in self.dd_date_values:
            return 'day'
        elif self._get_year_key() in self.dd_date_values:
            return 'month'
        return 'year'

    def get_context_data(self, **kwargs):
        date_field = self.dd_date_field
        date_type = self._get_dd_date_type()
        dates = self.get_queryset().dates(date_field, date_type)

        context = super(DateDrillDownMixin, self).get_context_data(**kwargs)

        context['dd_date'] = {
            'field': date_field,
            'type': date_type,
            'widget': DateDrillDownWidget(
                type=date_type,
                dates=dates,
                querydict=self.request.GET,
                field=date_field
            )
        }
        return context

    def get_queryset(self):
        queryset = super(DateDrillDownMixin, self).get_queryset()
        return queryset.filter(**self.dd_date_values)
