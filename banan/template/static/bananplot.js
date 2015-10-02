$(function() {
    var data = [ ["January", 10], ["February", 8], ["March", 4], ["April", 13], ["May", 17], ["June", 9] ];
    $.plot("#placeholder", [ data ], {
	series: {
	    bars: {
		show: true,
		barWidth: 0.6,
		align: "center"
	    }
	},
	xaxis: {
	    mode: "categories",
	    tickLength: 0,
	    font: { 
		color: "#ffffff" 
	    }
	},
	yaxis: {
	    font: { 
		color: "#ffffff" 
	    }
	},
	grid: {
	    color: "#ffffff"
	}
    });
 });
