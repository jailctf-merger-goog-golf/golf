// you have to set the safety key
let SAFETY_KEY = localStorage.getItem("goog-safety-key");
if (SAFETY_KEY == 'null') {
    SAFETY_KEY = null;
}
while (!SAFETY_KEY) {
    SAFETY_KEY = prompt("safety key (see pinned in discord)");
    localStorage.setItem("goog-safety-key", SAFETY_KEY);
    if (SAFETY_KEY) {
        alert("its stored in browser localStorage just so you know");
    }
}
SAFETY_KEY = SAFETY_KEY.trim()

let viewingTaskNum = parseInt(localStorage.getItem("goog-task") ?? "1");
let lastViewingTaskNum = viewingTaskNum;

// websockets stuff
let websocketTiming = -1;
let ignoreWebsocketUntil = -1;
let openToReceiving = true;
let websocket = new WebSocket("wss://goog-golf.pyjail.club/ws")
window.websocket = websocket;
websocket.onmessage = (event) => {
    let data = JSON.parse(event.data);
    if (data.type === "error") {
        alert("websocket error:", data.error_msg)
    }
    if (data.type == "set-listen-done") {
        openToReceiving = true;
    }
    if (typeof data.timing === "number") {
        websocketTiming = data.timing;
    }
    if (openToReceiving && websocketTiming > ignoreWebsocketUntil) {
        if (typeof data.solution === "string" && solutionView.state.doc.toString() !== data.solution) {
            solutionView.dispatch({ changes: { from: 0, to: solutionView.state.doc.length, insert: data.solution } })
        }
        if (typeof data.annotations === "string" && annotationsView.state.doc.toString() !== data.annotations) {
            annotationsView.dispatch({ changes: { from: 0, to: annotationsView.state.doc.length, insert: data.annotations } })
        }
    }
};
websocket.onopen = (event) => {
    websocketSendViewTask(taskElm.value*1)
};
let websocketSendViewTask = () => {
    websocket.send(JSON.stringify({"type": "set-listen", "task": viewingTaskNum, "safety_key": SAFETY_KEY}))
}
let websocketSendAnnotations = () => {
    if (annotationsView.hasFocus) {
        ignoreWebsocketUntil = websocketTiming+0.5;  // assume latency is 0.5 seconds at most
        websocket.send(JSON.stringify({
            "safety_key": SAFETY_KEY,
            "timing": websocketTiming,
            "type": "update",
            "task": viewingTaskNum,
            "annotations": annotationsView.state.doc.toString()
        }))
    }
}
let websocketSendSolution = () => {
    if (solutionView.hasFocus) {
        ignoreWebsocketUntil = websocketTiming+0.5;  // assume latency is 0.5 seconds at most
        websocket.send(JSON.stringify({
            "safety_key": SAFETY_KEY,
            "timing": websocketTiming,
            "type": "update",
            "task": viewingTaskNum,
            "solution": solutionView.state.doc.toString()
        }))
    }
}


// everything else
import {EditorView, basicSetup} from "codemirror"
import {python} from "@codemirror/lang-python"
import {oneDark} from "@codemirror/theme-one-dark"
import {coolGlow} from 'thememirror';


let randomUnsolved = document.getElementById('random-unsolved');
let resultElm = document.getElementById("result");
let taskElm = document.getElementById("task");
let previewElm = document.getElementById("preview");
let leftButton = document.getElementById("left");
let rightButton = document.getElementById("right");
let runButton = document.getElementById("run");


let updateEverythingAccordingToViewingTaskNum = async () => {
    if (websocket.readyState !== WebSocket.CONNECTING) {
        annotationsView.dispatch({ changes: { from: 0, to: annotationsView.state.doc.length, insert: "" } })
        solutionView.dispatch({ changes: { from: 0, to: solutionView.state.doc.length, insert: "" } })
        websocketSendViewTask()
        openToReceiving = false;
    }
    localStorage.setItem("goog-task", viewingTaskNum)
    taskElm.value = viewingTaskNum+[];
    resultElm.style.backgroundImage = "";
    while (resultElm.firstChild) { resultElm.firstChild.remove(); }
    previewElm.innerHTML = `<img src="/view/${viewingTaskNum}" class="max-width">`
}

let runTask = async () => {
    resultElm.style.backgroundImage = "";
    while (resultElm.firstChild) { resultElm.firstChild.remove(); }

    let resp = await fetch(`/run/${viewingTaskNum}`, {method: "POST", body: solutionView.state.doc.toString()})
    let text = await resp.text();

    // everything below is showing results
    if (resp.status != 200) {
        let newElm = document.createElement("p")
        if (resp.status == 500) {
            // return code wasn't 0, will get full stderr output
            newElm.innerText = "Got a runtime error:\n" + text;
        }
        else if (resp.status == 501) {
            // timeout error, should return a good error message
            newElm.innerText = text;
        }
        else if (resp.status == 502) {
            // unknown error
            newElm.innerText = "Got unknown error when running:\n" + text;
        }
        else {
            // unknown status code
            newElm.innerText = `Runner returned an unknown status code of ${resp.status}`
        }
        
        resultElm.appendChild(newElm);
        return;
    }

    if (text.includes("code IS NOT ready for submission")) {
        let imgsDiv = document.createElement('div')
        imgsDiv.classList.add('flex-horizontal')

        let expected = document.createElement("img")
        expected.setAttribute("src", `/working/expected/${String(viewingTaskNum).padStart(3,'0')}.png?` + Date.now())
        expected.classList.add("broken")
        imgsDiv.appendChild(expected);

        let actual = document.createElement("img")
        actual.setAttribute("src", `/working/actual/${String(viewingTaskNum).padStart(3,'0')}.png?` + Date.now())
        actual.classList.add("broken")
        imgsDiv.appendChild(actual);

        resultElm.appendChild(imgsDiv);
    }
    if (text.includes("code IS READY for submission")) {
        resultElm.style.backgroundImage = "url(https://i.etsystatic.com/28810262/r/il/2fc5e0/5785166966/il_fullxfull.5785166966_nvy4.jpg)"
    }

    let newElm = document.createElement("code")
    newElm.innerText = text;
    resultElm.appendChild(newElm);
    return;
}

runButton.addEventListener("click", (e) => {
    runTask()
})

randomUnsolved.addEventListener('click', async (e) => {
    alert("uhh todo add functionality on ws-server");
})


taskElm.addEventListener("keydown", (e) => {
    let prevTaskVal = taskElm.value;

    setTimeout(() => {
        if (!parseInt(taskElm.value)) {
            return;
        }
        if (![...Array(401).keys()].slice(1).includes(parseInt(taskElm.value))) {
            alert(`bad task value "${taskElm.value}"`);
            viewingTaskNum = parseInt(prevTaskVal);
        } else {
            viewingTaskNum = Math.min(Math.max(parseInt(taskElm.value), 1), 400)
        }
        updateEverythingAccordingToViewingTaskNum()
    }, 20)
})
leftButton.addEventListener("click", (e) => {
    viewingTaskNum = (viewingTaskNum + 398) % 400 + 1
    updateEverythingAccordingToViewingTaskNum()
})
rightButton.addEventListener("click", (e) => {
    viewingTaskNum = (viewingTaskNum + 400) % 400 + 1
    updateEverythingAccordingToViewingTaskNum()
})

const theme = EditorView.theme({
  "&": {
    fontSize: "12pt",
    border: "1px solid #c0c0c0"
  },
});

let solutionListen = EditorView.updateListener.of((v) => {
    if (v.docChanged) {
        websocketSendSolution()
    }
})
const solutionView = new EditorView({
  parent: document.getElementById("editor"),
  doc: "",
  extensions: [basicSetup, python(), oneDark, [theme], solutionListen],
})

let annotationsListen = EditorView.updateListener.of((v) => {
    if (v.docChanged) {
        websocketSendAnnotations()
    }
})
const annotationsView = new EditorView({
  parent: document.getElementById("annotations"),
  doc: "",
  extensions: [basicSetup, python(), coolGlow, [theme], annotationsListen],
})

window.theme = theme;
window.solutionView = solutionView;
window.annotationsView = annotationsView;

updateEverythingAccordingToViewingTaskNum()
