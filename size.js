const mapContainer = document.querySelector("body")

let w_width = document.body.clientWidth;
let w_height = document.body.clientHeight;

function reRender(){
    w_width = document.body.clientWidth;
    w_height = document.body.clientHeight;
    console.log(w_width);
    console.log(w_height);
}

window.addEventListener('resize',reRender)