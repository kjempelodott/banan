function clickEvent(button) {
    // If already active, do nothing
    if (button.className == 'active') {
	return false;
    }

    // Deactivate other button(s) and activate clicked button
    var span = button.closest('span');
    var buttons = span.childNodes;
    for (i in buttons) {
	if (buttons[i].className == 'active') {
	    buttons[i].className = 'inactive'
	}
    }
    button.className = 'active';

    // Change visibility
    if (button.id == 'label-btn') {
	// Enable
	getElem('period').style.display = 'block';
	// Disable
	getElem('labels').style.display = 'none';
    }
    else if (button.id == 'year-btn' || button.id == 'month-btn') {
	// Enable
	getElem('labels').style.display = 'block';
	// Disable
	getElem('period').style.display = 'none';
    }
    // A label button was pressed
    else {
	postQuery();
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


