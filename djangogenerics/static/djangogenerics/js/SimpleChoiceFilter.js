var url_params = {};
(function () {
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, ' ')); },
        query  = window.location.search.substring(1);

    while (match = search.exec(query)) {
       url_params[decode(match[1])] = decode(match[2]);
    }
})();


function simple_choice_filter_changed(widget) {
    var key = widget.name, value = widget.options[widget.selectedIndex].value;
    if ('' == value) {
        delete url_params[key];
    }
    else {
        url_params[key] = value;
    }
    // console.log(generate_full_url_with_params(url_params));
    window.location = generate_full_url_with_params(url_params);
}

function generate_full_url_with_params(obj) {
    var parts = [];
    for (var i in obj) {
        if (obj.hasOwnProperty(i)) {
            parts.push(encodeURIComponent(i) + '=' + encodeURIComponent(obj[i]));
        }
    }
    query_string = parts.join('&');
    if (query_string.length > 0)
        query_string = '?' + query_string;
    return window.location.href.split('?')[0] + query_string;
}
