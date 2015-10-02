$(function() {
    $('a').click(function() {

	var elem = this;

	var queryVar = elem.closest('span').className;
	var queryString =  queryVar + '=' + elem.id;
	console.log(queryString);
	$.ajax({
	    type: 'POST',
	    url: '',
	    contentType: 'text/plain',
	    data: queryString,
	    success: function() {
		$('.' + queryVar + ' .active').attr('class', 'inactive');
		elem.className = 'active';

		if (queryVar == 'foreach') {
		    if (elem.id == 'label') {
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
	    }
	});
	return false;
    });
});
