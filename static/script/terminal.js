const term = new Terminal({
    cursorBlink: true,
    macOptionIsMeta: true,
    scrollback: true,
});
term.attachCustomKeyEventHandler(customKeyEventHandler);
// https://github.com/xtermjs/xterm.js/issues/2941
const fit = new FitAddon.FitAddon();
term.loadAddon(fit);
term.loadAddon(new WebLinksAddon.WebLinksAddon());
term.loadAddon(new SearchAddon.SearchAddon());

term.open(document.getElementById("terminal"));
fit.fit();
term.resize(17, 50);
console.log(`size: ${term.cols} columns, ${term.rows} rows`);
fit.fit();
term.writeln("Welcome to PCDS Console");
term.writeln('')
term.writeln("You can copy with ctrl+shift+x");
term.writeln("You can paste with ctrl+shift+v");
term.writeln('Do not type EXIT or exit, if you want to exit just close the tab')
term.writeln('')
term.onData((data) => {
    console.log("browser terminal received new data:", data);
    socket.emit("pty-input", { input: data });
});

const socket = io.connect("/pty");
const status = document.getElementById("status");

socket.on("pty-output", function (data) {
    console.log("new output received from server:", data.output);
    term.write(data.output);
});

socket.on("connect", () => {
    fitToscreen();
    status.innerHTML =
        '<span style="background-color: lightgreen;">connected</span>';
});

socket.on("disconnect", () => {
    status.innerHTML =
        '<span style="background-color: #ff8383;">disconnected</span>';
});

function fitToscreen() {
    fit.fit();
    const dims = { cols: term.cols, rows: term.rows };
    console.log("sending new dimensions to server's pty", dims);
    socket.emit("resize", dims);
}

function debounce(func, wait_ms) {
    let timeout;
    return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait_ms);
    };
}

/**
 * Handle copy and paste events
 */
function customKeyEventHandler(e) {
    if (e.type !== "keydown") {
        return true;
    }
    if (e.ctrlKey && e.shiftKey) {
        const key = e.key.toLowerCase();
        if (key === "v") {
            navigator.clipboard.readText().then((toPaste) => {
                term.writeText(toPaste);
            });
            return false;
        } else if (key === "c" || key === "x") {
            const toCopy = term.getSelection();
            navigator.clipboard.writeText(toCopy);
            term.focus();
            return false;
        }
    }
    return true;
}

const wait_ms = 50;
window.onresize = debounce(fitToscreen, wait_ms);