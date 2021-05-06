function clickEvent(button) {
    // If already active, do nothing
    if (button.className == 'active') {
	    return false;
    }

    var views = document.getElementsByClassName('view');
    Array.prototype.forEach.call(views, function(elem, index) {
        elem.style.visibility = 'hidden';
        elem.style.display = 'none';
    });

    // Deactivate other button(s) and activate clicked button
    var span = button.closest('span');
    var buttons = span.childNodes;
    for (i in buttons) {
	    if (buttons[i].className == 'active') {
	        buttons[i].className = 'inactive'
	    }
    }
    button.className = 'active';

    var view;
    // Change visibility
    if (button.id == 'label-btn') {
	    // Enable
	    getElem('period').style.display = 'block';
	    // Disable
	    getElem('labels').style.display = 'none';
        view = getElem('label-view');
    }
    else if (button.id == 'year-btn' || button.id == 'month-btn') {
	    // Enable
	    getElem('labels').style.display = 'block';
	    // Disable
	    getElem('period').style.display = 'none';
        if (button.id == 'year-btn') {
            view = getElem('year-view');
        }
        else {
            view = getElem('month-view');
        }
        postQuery();
    }
    // A label button was pressed
    else {
	    postQuery();
    }
    if (view) {
        view.style.visibility = 'visible';
        view.style.display = 'inline';
    }
    return false;
}

function keyEvent(e) {
    // Enter button
    if (e.keyCode == 13) {
	postQuery();
    }
    return false;
}


