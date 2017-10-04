function print(view, text, sums) {
    var frame = view.getElementsByClassName('text')[0];
    frame.innerHTML = '';
    var keys = Object.keys(text).sort();
    for (i in keys) {
	var key = keys[i]

	var header = document.createElement('h2');
	header.innerHTML = key;
	frame.appendChild(header);

	var table = document.createElement('table');
	for (j in text[key]) {
	    var row = table.insertRow();
	    for (k in text[key][j]) {
		row.insertCell().innerHTML = text[key][j][k];
	    }
	}
	frame.appendChild(table);
    }
}


function postQuery() {

    var query = {};
    var view = null;
    if (getElem('label-btn').className == 'active') {
	var from = getElem('fromPeriod');
	var to = getElem('toPeriod');
	if (from.textLength < 6) {
	    return false;
	}
	query['period'] = fromPeriod.value + '-' + toPeriod.value;
	view = getElem('label-view');
    }
    else  {
	if (getElem('month-btn').className == 'active') {
	    query['period'] = 'month';
	    view = getElem('month-view');	    
	}
	else if (getElem('year-btn').className == 'active') {
	    query['period'] = 'year';
	    view = getElem('year-view');
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
		print(view, data['text']);
	    }
	);
    return true;
}
