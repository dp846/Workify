function updateTime () { // increment time for the timer
    seconds++;

    if (seconds === 60) {
        seconds = 0;
        minutes++;

        if (minutes === 60) {
            minutes = 0;
            hours ++;
        }
    }

    return [hours, minutes, seconds];
}

function setTime(time){
    document.getElementsByClassName("time")[0].innerHTML = time[0].toString().padStart(2, '0') + ":" + time[1].toString().padStart(2, '0') + ":" + time[2].toString().padStart(2, '0');
}

function runTime(){
    time = updateTime();
    if (seconds % 60 == 0) {
        progressElm.style.strokeDashoffset -= circum;
    }
    progressElm.style.strokeDashoffset -= circum/60;    
    setTime(time);
}

document.getElementsByClassName("active")[0].classList.remove("active");
document.getElementById("timer_link").classList.add("active");

var progressElm = document.getElementsByClassName('progress')[0];
var circum = 2 * Math.PI * progressElm.getAttribute('r');

progressElm.style.strokeDasharray = circum;
progressElm.style.strokeDashoffset = -circum;

var seconds = 0;
var minutes = 0;
var hours = 0;
var timer;

document.getElementById("pause").onclick = function() {pause()};
document.getElementById("restart").onclick = function() {restart()};
document.getElementById("start").onclick = function() {startStop(this)};

function startStop(button) {
    if (button.innerHTML === "START") {
        timer = setInterval(() => {runTime()}, 1000);
        button.innerHTML = "STOP";
    } else {
        clearInterval(timer);
        button.innerHTML = "START";
        document.getElementById("submit_session").style.visibility = "visible";
        document.getElementById("time_elapsed").value = hours + ":" + minutes + ":" + seconds;
    }
}
function pause(){
    clearInterval(timer);
    document.getElementById("start").innerHTML = "START";
}

function restart(){
    clearInterval(timer);
    document.getElementById("start").innerHTML = "START";
    progressElm.style.strokeDashoffset = -circum;
    seconds = 0;
    minutes = 0;
    hours = 0;
    setTime([0,0,0]);
}

var rangeslider = document.getElementById("sliderRange");
var output = document.getElementById("value");
output.innerHTML = rangeslider.value;

rangeslider.oninput = function() {
output.innerHTML = this.value;
}

/*deal with text of button - flip between START-STOP, add funtionality for pause later?*/
// document.getElementById("button").onclick = function() {
   /* const currentDate = new Date(); const timestamp = currentDate. getTime(); */
// };

// var seconds = 0;
// var minutes = 0;
// var hours = 0;

// var d_seconds = 0;
// var d_minutes = 0;
// var d_hours = 0;

// var time; // used for display

// var startFlag = false;
// var startDate;


// function startTimer () {
//     startDate = Date.now();
//     time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds(); 
//     startFlag = true;
// }

// function endTime () {
//     startFlag = false;
//     // reset timer values
//     seconds = 0;
//     minutes = 0;
//     hours = 0;
//     duration = (startDate - Date.now())/60000; // duration in minutes
// }

// while (startFlag) {
//     window.setInterval(runTime,1000);
// }
