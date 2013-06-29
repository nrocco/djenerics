function execute_mass_action()
{
    var selected_action = document.getElementById('id__selected_action');
    if (selected_action[selected_action.selectedIndex].value == '') {
        return false;
    }

    var _ids = [], inputs = document.getElementsByClassName('_id');
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked) {
            _ids.push(inputs[i].value);
        }
    }

    if (_ids.length == 0) {
        return false;
    }

    var selected_objects = document.getElementById('id__selected_objects');
    selected_objects.value = _ids.join();
    return true;
}
