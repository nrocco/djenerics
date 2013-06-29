jQuery(document).ready(function($)
{
  function onSelectForeignKeyAutoCompleteWidget(event, data)
  {
    console.debug('typeahead:selected', event, data);
    var store = $('#' + $(event.currentTarget).attr('data-store'));

    console.debug('changing primary key in the store from', store.val(), 'to', data.id);
    store.val(data.id);
  };

  console.debug('Loading djangojax javascript');

  $('.djangojax-fkac').each(function()
  {
    var fkac_widget = $(this);
    console.debug('Found djangojax widget', fkac_widget);

    fkac_widget.typeahead({
      remote: fkac_widget.attr('data-remote'),
      valueKey: fkac_widget.attr('data-key'),
      name: 'djangojax-fkac-' + fkac_widget.attr('data-store'),
      limit: 15,
      minLength: 2
    }).on('typeahead:selected', onSelectForeignKeyAutoCompleteWidget);
  });
});
