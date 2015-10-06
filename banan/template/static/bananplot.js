$(function() {
    $.post('', '', function(data) { plot(data) });
    return false;
})


function plot(data) {
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
    });console.log(data); 
 };
