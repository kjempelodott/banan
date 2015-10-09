$(function() {
    $('a').click(function() {

	// if already active, do nothing
	var button = this;
	if (button.className == 'active') {
	    return false;
	}

	// deactivate other button and activate clicked button
	var span = button.closest('span').className;
	$('.' + span + ' .active').attr('class', 'inactive');
	button.className = 'active';

	// change visibility stuff
	if (span == 'foreach') {
	    if (button.id == 'label') {
		$('#average').css('visibility', 'visible');
		$('#labels').css('display', 'none');
		$('#labels').className = 'inactive';
		$('#period').css('display', 'inline');
	    }
	    else {
		$('#average').css('visibility', 'hidden');
		$('#period').css('display', 'none');
		$('#period').className = 'inactive';
		$('#labels').css('display', 'inline');
	    }
	}
	
	// prepare post data
	var query = {}
	$('a.active').each(function(index) {
	    var elem = this;
	    var queryVar = elem.closest('span').className;
	    query[queryVar] = elem.id;
	});

	// post and plot or print data
	$.post('', query,
	       function(data) {
		   if ($('.datatype .active')[0].id == 'plot') {
		       plot(data);
		   }
		   else {
		       console.log('make text function');
		       print(data);
		   }
	       });
	return false;
    })
})
