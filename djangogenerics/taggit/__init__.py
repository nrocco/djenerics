from taggit.forms import TagWidget, TagField

class AutoCompleteTagWidget(TagWidget):
    def __init__(self, endpoint, *args, **kwargs):
        super(AutoCompleteTagWidget, self).__init__(*args,**kwargs)
        self.attrs['class'] = 'tags_autocomplete_widget'
        self.attrs['data-source'] = endpoint

    class Media:
        js = ('djangogenerics/js/tags_autocomplete_widget.js',)


class AutoCompleteTagField(TagField):
    widget = AutoCompleteTagWidget

    def __init__(self, endpoint, *args, **kwargs):
        widget = kwargs.get("widget", False)
        if not widget or not isinstance(widget, AutoCompleteTagWidget):
            kwargs["widget"] = AutoCompleteTagWidget(endpoint=endpoint)
        super(AutoCompleteTagField, self).__init__(*args, **kwargs)
