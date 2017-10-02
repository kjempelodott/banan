function getElem(elementId) {
    return document.getElementById(elementId);
}

function init() {
    // Get data from previous month
    var date = new Date();
    var month = date.getUTCMonth();
    var year = date.getUTCFullYear();
    if (!month) {
	month = 12;
	year -= 1;
    }

    month = ('0' + month.toString()).slice(-2);
    year = year.toString();

    getElem('fromPeriod').value = month + year;
    postQuery();

    // Get list of all labels
    fetch('/labels.json').then(
	function(response) {
	    return response.json();
	}).then(
	    function(labels) {
		var span = document.getElementById('labels');
		for (i in labels) {
		    var label = labels[i];
		    var button = document.createElement('a');
		    button.className = 'inactive';
		    button.id = label;
		    button.innerHTML = label;
		    button.onclick = function () {
			return clickEvent(this)
		    };
		    span.appendChild(button);
		}
	    }
	);
}
