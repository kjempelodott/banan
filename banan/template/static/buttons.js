$(function() {
    $('a').click(function() {

	var elem = this;
	if (elem.className == 'active') {
	    return false;
	}

	var queryVar = elem.closest('span').className;
	var queryString =  queryVar + '=' + elem.id;

	$.post('', queryString,
	       function(data) {
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
		   plot(data);
	       });

	return false;
    });
});
