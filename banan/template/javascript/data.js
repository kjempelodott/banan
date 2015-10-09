function isValid() {
    if ($('#label')[0].className == 'active') {
	if ($('#labels')[0].className == 'active') {
	    return false;
	}
    }
    else {
	if ($('#input')[0].className == 'active') {
	    return false;
	}
	if ($('#average')[0].className == 'active') {
	    return false;
	}
	if (!$('.select .active .active').length) {
	    return false;
	}
    }
    return true;
}


function print(data) {

    var frame = $('#placeholder');
    frame.html('');
    frame.css('font-family', 'monospace');
    frame.css('font-size', '.6em');

    var keys = Object.keys(data);
    keys.sort();
    $.each(keys, function(index, key) {
	frame.append('<div>[' + key.replace(/([ ])/g, '&nbsp;') + ']<\div><br>');
	$.each(data[key], function(index, val) {
	    frame.append('<div>' + val.replace(/([ ])/g, '&nbsp;') + '<\div>');
	}); 
	frame.append('<br>');
    });
}


function plot(data) {

    var positive = { data: [], color: '#3fa46a' };
    var negative = { data: [], color: '#cd4436' };
    var length = 0;

    var keys = Object.keys(data);
    keys.sort();    
    $.each(keys, function (index, key) {
	var val = data[key]
	length += 1;
	if (val > 0) { 
	    positive.data.push([key, val]);
	    negative.data.push([key, 0]);
	}
	else {
	    positive.data.push([key, 0]);
	    negative.data.push([key, -val]);
	}
    });   		 
    

    var frame = $('#placeholder');
    frame.html('');
    frame.css('font-family', '');
    frame.css('font-size', '.8em');

    $.plot('#placeholder', [ positive, negative ] , {
	series: {
	    bars: {
		show: true,
		barWidth: 0.7,
		align: 'center'
	    }
	},
	xaxis: {
	    mode: 'categories',
	    tickLength: 0,
	    font: { 
		color: '#ffffff' 
	    }
	},
	yaxis: {
	    font: { 
		color: '#ffffff' 
	    }
	},
	grid: {
	    color: '#ffffff'
	}
    });
}


function getData() {

    if (!isValid()) {
	return false;
    }

    var query = {};
    $('a.active').each(function(index, elem) {
	var queryVar = elem.closest('span').className;
	query[queryVar] = elem.id;
    });
    
    var select = $('.select .active');
    if (select.id == 'labels') {
	query['select'] = $('.select .active .active').val();
    }
    else {
	query['select'] = $('#period').val();
    }

    // post and plot or print data
    $.post('', query,
	   function(data) {
	       if ($('.datatype .active')[0].id == 'plot') {
		   plot(data);
	       }
	       else {
		   print(data);
	       }
	   })
    
	.fail(function() {
	    var frame = $('#placeholder');
	    frame.html('BAD REQUEST :(');
	});
}
