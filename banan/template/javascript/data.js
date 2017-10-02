function print(data) {

    var frame = $('text');
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


function postQuery() {

    var query = {};
    if (getElem('label-btn').className == 'active') {
	var from = getElem('fromPeriod');
	var to = getElem('toPeriod');
	if (from.textLength < 6) {
	    return false;
	}
	query['period'] = fromPeriod.value + '-' + toPeriod.value;
    }
    else  {
	if (getElem('month-btn').className == 'active') {
	    query['period'] = 'month';
	}
	else if (getElem('year-btn').className == 'active') {
	    query['period'] = 'year';
	}
	else {
	    return false;
	}
	var labelsArr = Array.prototype.slice.call(getElem('labels').childNodes);
	var selectedLabels = labelsArr.filter(l => l.className == 'active');
	var asStr = selectedLabels.map(l => l.id).join(',');
	if (asStr.length == 0) {
	    return false;
	}
	query['labels'] = asStr;
    }

    fetch('', {
	method: 'post',
	headers: new Headers({
		'Content-Type': 'x-www-form-urlencoded'
	}),
	body: JSON.stringify(query)
    }).then(
	function(response) {
	    return response.json();
	}).then(
	    function(data) {
		;
	    }
	);
    return true;
}
