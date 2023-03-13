var r = document.querySelector(':root');
let links = document.getElementsByClassName("link");
    
function hover(item){
    for (let i = 0; i < links.length; i++) {
        links[i].style.opacity=0.5;
    }
    item.style.opacity=1;
    item.style.animation="grow .3s ease-out forwards";
}
function exit(item){
    for (let i = 0; i < links.length; i++) {
        links[i].style.opacity=1;
    }
    item.style.animation=0;
}


for (let i = 0; i < links.length; i++) {
    links[i].addEventListener("mouseover", function( event ) {hover(links[i]);}, false);
}
for (let i = 0; i < links.length; i++) {
    links[i].addEventListener("mouseout", function( event ) {exit(links[i]);}, false);
}