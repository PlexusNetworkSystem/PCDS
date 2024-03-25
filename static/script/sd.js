var theCount;
var alarm = document.getElementById("alarm");
var panel = document.getElementById("panel");
var turnOff = document.getElementById("turn-off");
var turnOffHor = document.getElementById("closing");
var detonate = document.getElementById("detonate");
alarm.volume = 0.5; //volume level - (changed from 0.25 to 0.5)

var time = document.getElementById("time");


function selfdestruct() {
    fetch('/panelcmd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token,
            process: 'selfdestruct'
        })
    })
        .then(response => response.json())
        .catch(error => {
            console.error('Error:', error);
        });
}

function showCountDown() {
    time.innerText = time.innerText - 1;
    if (time.innerText == 0) {
        clearInterval(theCount);
        time.classList.add("crono");
        abort.classList.add("hide");
        detonate.classList.add("show");
        setTimeout(function () {
            turnOff.classList.add("close");
            turnOffHor.classList.add("close");
            reload.classList.add("show");
            alarm.pause();
            selfdestruct();
        }, 1500);
    }
}

var cover = document.getElementById("cover");
cover.addEventListener("click", function () {
    if (this.className == "box") this.classList.add("opened");
    else this.classList.remove("opened");
});

var docElm = document.documentElement;
var btn = document.getElementById("activate");
activate.addEventListener("click", function () {
    this.classList.add("pushed");
    alarm.load();
    alarm.currentTime = 10.1;
    alarm.play();
    docElm.requestFullscreen();
    setTimeout(function () {
        panel.classList.add("show");
        theCount = setInterval(showCountDown, 1000);
        alarm.load();
        alarm.play();
    }, 500);
});

var abort = document.getElementById("abort");
abort.addEventListener("click", function () {
    btn.classList.remove("pushed");
    panel.classList.remove("show");
    clearInterval(theCount);
    document.exitFullscreen();
    time.innerText = 9;
    alarm.pause();
    alarm.currentTime = 10;
    alarm.play();
});

var reload = document.getElementById("restart");
reload.addEventListener("click", function () {
    panel.classList.remove("show");
    turnOff.classList.remove("close");
    turnOffHor.classList.remove("close");
    abort.classList.remove("hide");
    detonate.classList.remove("show");
    cover.classList.remove("opened");
    btn.classList.remove("pushed");
    this.classList.remove("show");
    time.classList.remove("crono");
    time.innerText = 9;
});

setTimeout(function () {
    cover.classList.remove("opened");
}, 100);