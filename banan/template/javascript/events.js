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
	    $('#sum').attr('class', 'active');
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
    // selects the inputs fromPeriod and toPeriod
    $('input').keydown(function(e) {
	// enter button
	if (e.keyCode == 13) {
	    getData();
	}
	return true;
    });
});


