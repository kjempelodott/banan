$(function() {
    $.post('', '', function(data) { plot(data) });
    return false;
})

function print(data) {

    var frame = $('#placeholder');
    frame.html('');
    frame.css('font-family', 'monospace');

    $.each(data, function(key, val) {
	frame.append('<div>[' + key.replace(/([ ])/g, '&nbsp;') + ']<\div><br>');
	$.each(val, function(index) {
	    frame.append('<div>' + this.replace(/([ ])/g, '&nbsp;') + '<\div>');
	}); 
	frame.append('<br>');
    });
}

function plot(data) {

    var positive = { data: [], color: '#3fa46a' };
    var negative = { data: [], color: '#cd4436' };
    
    $.each(data, function (key, val) {
	if (val > 0) { 
	    positive.data.push([key, val]);
	    negative.data.push([key, 0]);
	}
	else {
	    positive.data.push([key, 0]);
	    negative.data.push([key, -val]);
	}
    });   		 
    // barwidth = .8 * placeholder width / len(data)

    $('#placeholder').css('font-family', '');

    $.plot('#placeholder', [ positive, negative ] , {
	series: {
	    bars: {
		color: '#00ff00',
		show: true,
		barWidth: 0.6,
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

