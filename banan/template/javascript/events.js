function clickEvent(button) {

    // if already active, do nothing
    if (button.className == 'active') {
	return false;
    }

    // deactivate other button(s) and activate clicked button
    var span = button.closest('span').className;
    $('.' + span + ' .active').attr('class', 'inactive');
    button.className = 'active';

    // change visibility
    if (span == 'foreach') {
	if (button.id == 'label') {
	    // enable
	    $('#average').css('visibility', 'visible');
	    $('#input').css('display', 'block');
	    //disable
	    $('#labels').css('display', 'none');
	    $('#labels .active').attr('class', 'inactive');
	}
	else {
	    //enable
	    $('#labels').css('display', 'block');
	    // disable
	    $('#average').css('visibility', 'hidden');
	    $('#average').attr('class', 'inactive');
	    $('#input').css('display', 'none');
	}
    }
    
    getData();
    return false;
}


$(function() {
    $('a').click(function() {
	return clickEvent(this);
    });
});


$(function() {
    $('#period').keydown(function(e) {
	// enter
	if (e.keyCode == 13) {
	    getData();
	    return true;
	}
	// do default for f#, backspace, delete, navigation, alt, ctrl and meta
	if ((e.keyCode > 111 && e.keyCode < 124) ||
	    e.keyCode == 8 || e.keyCode == 46 ||
	    e.keyCode == 35 || e.keyCode == 36 ||
	    e.keyCode == 37 || e.keyCode == 39 ||
	    e.altKey || e.ctrlKey || e.metaKey) {
	    return true;
	}
	// ignore all but numbers
	var charCode = e.key.charCodeAt()
	if (charCode < 48 || charCode > 58) {
	    return false;
	}
	
	var period = this;
	if (period.textLength == 6) {
	    period.value += '–';
	}
	return true;
    });
});


