Snippets = window.Snippets || {};

(function(S, $) {

    var TagCompletion = function(options) {
        this.options  = options || {};
        this.defaults = {'min_length':2};
        this.min_length = this.options.min_length || this.defaults.min_length;
    };

    TagCompletion.prototype.split = function(value) {
        return value.split(/,\s*/);
    };

    TagCompletion.prototype.pop_tag = function(value) {
        return this.split(value).pop();
    };

    TagCompletion.prototype.bind_to = function(element) {
        var self = this;
        this.input_element = $(element);
        this.endpoint = this.input_element.attr('data-source');
        this.input_element.autocomplete({
            'source': function(request,response){self.process(request,response);},
            'search': function() {
                // custom minLength
                var term = self.pop_tag( this.value );
                if ( term.length < self.min_length ) {
                    return false;
                }
            },
        });
    };
    
    TagCompletion.prototype.process = function(request,response) {
        var url = this.endpoint,
            term = request.term,
            pieces = this.split(term),
            new_term = '',
            last_piece = pieces.pop();
        
        if (!last_piece)
            response([]);

        if (pieces.length > 0)
            new_term = pieces.join(', ') + ', ';

        $.getJSON(url, {'term':last_piece}, function(data) {
            var results = [];
            $.each(data, function(k, v) {
                v.label = v.name,
                v.value = new_term + v.name + ", ";
                results.push(v);
            });
            response(results);
        });
    };
        
    S.TagCompletion = TagCompletion;

})(Snippets, django.jQuery);


django.jQuery(document).ready(function($) {
    var tag_completion = new Snippets.TagCompletion()
    tag_completion.bind_to('.tags_autocomplete_widget');
});

