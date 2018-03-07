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

function plot(view, graph, sums) {
    var frame = view.getElementsByClassName('graph')[0];
    frame.innerHTML = '';
    var keys = Object.keys(graph).sort();
    var scale = Math.max(...Object.values(graph).map(Math.abs));
    for (i in keys) {
	var key = keys[i]
	if (key.slice(-1) == '*') {
	    continue;
	}

	var bar = document.createElement('div');
	if (graph[key] > 0) {
	    bar.className = 'bar positive';
	}
	else {
	    bar.className = 'bar negative';
	}
	bar.style.width = (70 * Math.abs(graph[key])/scale).toString() + '%';

	var label = document.createElement('span');
	label.className = 'label';
	label.innerHTML = '<p>' + key + '</p>';
	bar.appendChild(label);

	var amount = document.createElement('span');
	amount.className = 'amount';
	amount.innerHTML = '<p>' + graph[key].toFixed(2) + '</p>';
	bar.appendChild(amount);

	frame.appendChild(bar);
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
	var selectedLabel = labelsArr.find(l => l.className == 'active');
	var asStr = selectedLabel.id;
	if (asStr.length == 0) {
	    return false;
	}
	query['label'] = asStr;
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
		plot(view, data['graph']);
	    }
	);
    return true;
}
