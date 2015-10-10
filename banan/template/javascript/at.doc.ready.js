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

    // Get list of all labels
    $.get('labels.json', function(labels) {
	labels.sort();
	var div = $('.dataselect')[0];
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

	    var newElem = $('<a class="inactive" id="' + label + '">' + label + '</a>').appendTo(span);
	    newElem[0].onclick = function () { return clickEvent(this) };
	});
    });

    return false;
})
