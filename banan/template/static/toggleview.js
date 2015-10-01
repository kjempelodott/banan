function hide(id) {
    document.getElementById(id).style.visibility = 'hidden';
}

function show(id) {
    document.getElementById(id).style.visibility = 'visible';
}

function switch(on, off) {
    document.getElementById(off).style.display = 'none';
    document.getElementById(on).style.display = 'block';
}
