$(function() {

    // get data from previous month
    var date = new Date();
    var month = date.getUTCMonth();
    var year = date.getUTCFullYear();
    if (!month) {
	month = 12;
	year -= 1;
    }

    month = ('0' + month.toString()).slice(-2);
    year = year.toString();

    $('#period').val(month + year);
    getData();

    $.get('labels.json', function(labels) {
	labels.sort();
	var div = $('.select')[0];
	var span = $('#labels');
	lineWidth = 0;
	maxWidth = div.offsetWidth;

	$.each(labels, function(index, label) {

	    tmp = $('<div>' + label + '</div>').css(
		{'position': 'absolute', 
		 'float': 'left', 
		 'visibility': 'hidden'}).appendTo($('body'));

	    delta = 1.2 * tmp.width();

	    if (lineWidth + delta >= maxWidth) {
		span.append('<br>');
		lineWidth = 0;
	    }
	    
	    tmp.remove()
	    lineWidth += delta;

	    span.append('<a class="inactive">' + label + '</a>');
	});

	$.each(span.children, function(index, elem) {
	    elem.addEventListener('click', eventClick, false);
	});
    });

    return false;
})
