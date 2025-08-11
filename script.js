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
let refreshAsapMessageGiven = false;
let websocketTiming = -1;
let ignoreWebsocketUntil = -1;
let receivedKnown = 0;
let openToReceiving = true;
let websocket = new WebSocket("wss://goog-golf.pyjail.club/ws")
window.websocket = websocket;
websocket.onmessage = (event) => {
    let data = JSON.parse(event.data);
    if (data.type === "error") {
        alert("websocket error: " + data.error_msg)
    }
    if (data.type == "set-listen-done") {
        openToReceiving = true;
    }
    if (data.type == "random-unsolved" || data.type == "random-negative") {
        viewingTaskNum = data.task ?? 1;
        updateEverythingAccordingToViewingTaskNum()
    }
    if (data.type == "download-zip") {
        function base64ToArrayBuffer(base64) {
            var binaryString = window.atob(base64);
            var binaryLen = binaryString.length;
            var bytes = new Uint8Array(binaryLen);
            for (var i = 0; i < binaryLen; i++) {
               var ascii = binaryString.charCodeAt(i);
               bytes[i] = ascii;
            }
            return bytes;
         }

        function saveByteArray(reportName, byte) {
            var blob = new Blob([byte], {type: "application/zip"});
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            var fileName = reportName;
            link.download = fileName;
            link.click();
        };

        let sampleArr = base64ToArrayBuffer(data.zip);
        saveByteArray(`export-${Math.floor(Date.now()/1000)}.zip`, sampleArr);
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
        if (typeof data.known === "number") {
            receivedKnown = data.known;
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
let websocketSendSolution = (force=false) => {
    if (solutionView.hasFocus || force) {
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
let websocketSendRandomUnsolvedRequest = () => {
    websocket.send(JSON.stringify({
        "safety_key": SAFETY_KEY,
        "type": "random-unsolved"
    }))
}
let websocketSendRandomNegativeRequest = () => {
    websocket.send(JSON.stringify({
        "safety_key": SAFETY_KEY,
        "type": "random-negative"
    }))
}
let websocketSendDownloadZipRequest = () => {
    websocket.send(JSON.stringify({
        "safety_key": SAFETY_KEY,
        "type": "download-zip"
    }))
}


// everything else
import {EditorView, basicSetup} from "codemirror"
import {python} from "@codemirror/lang-python"
import {oneDark} from "@codemirror/theme-one-dark"
import {coolGlow} from 'thememirror';


let longTimeout = document.getElementById('long-timeout');
let randomUnsolved = document.getElementById('random-unsolved');
let randomNegative = document.getElementById('random-negative');
let downloadZip = document.getElementById('download-zip');
let resultElm = document.getElementById("result");
let taskElm = document.getElementById("task");
let previewElm = document.getElementById("preview");
let leftButton = document.getElementById("left");
let rightButton = document.getElementById("right");
let runButton = document.getElementById("run");
let viewGenCode = document.getElementById("view-gen-code");
let charCount = document.getElementById('char-count');
let knownCount = document.getElementById('known-count');
let copyTestcaseButtons = document.getElementById('copy-testcase-buttons');
let copyTestcaseButtonsLabel = document.getElementById('copy-testcase-buttons-label');
let copySol = document.getElementById('copy-sol')
let pasteSol = document.getElementById('paste-sol')
let openToolsDialog = document.getElementById('open-tools-dialog');
let toolsDialog = document.getElementById('tools');
let toolsUpdate = document.getElementById('tools-update');
let toolsLabel = document.getElementById('tools-label');
let toolsError = document.getElementById('tools-error');
let toolsOptions = document.getElementById('tools-options');
let toolsDialogClose = document.getElementById('tools-close');


let updateToolsDialogOptions = async () => {
    let resp = await fetch("/tools/list")
    if (resp.status != 200) {
        alert(await resp.text())
        return;
    }
    let options = await resp.json();
    while (toolsOptions.firstChild) { toolsOptions.firstChild.remove(); }
    for (let option of options) {
        let compOption = document.createElement("div");
        compOption.classList.add("tools-option")
        compOption.classList.add("fancy-button")
        compOption.innerText = option;
        compOption.addEventListener("click", async () => {
            toolsError.innerText = '';
            toolsLabel.innerText = 'Running ' + option;
            let resp2 = await fetch("/tools/run/"+option,
                {method: "POST", body: [...solutionView.state.doc.toString()].map(q => q.charCodeAt(0).toString(16).padStart(2, '0')).join("")}
            )
            if (resp2.status !== 200) {
                toolsError.innerText = "status: " + resp2.status + "\n" + await resp2.text();
                toolsLabel.innerText = 'Tools';
                return;
            }

            let data2 = await resp2.json();

            function hexToBytes(hex) {
                hex = hex.replaceAll(/[^0-9a-f]/g, '');
                let bytes = "";
                for (let c = 0; c < hex.length; c += 2) {
                    bytes += (String.fromCharCode(parseInt(hex.substr(c, 2), 16)));
                }
                return bytes;
            }
            let inp = hexToBytes(data2.stdout);
            solutionView.dispatch({ changes: { from: 0, to: solutionView.state.doc.length, insert: inp } })
            ignoreWebsocketUntil = websocketTiming+0.7;
            websocketSendSolution(true);

            toolsError.innerText = data2.stderr;
            toolsLabel.innerText = 'Tools';
        });
        toolsOptions.appendChild(compOption);
    }
}

openToolsDialog.addEventListener("click", (e) => {
    toolsDialog.showModal();
    toolsError.innerText = '';
    toolsLabel.innerText = 'Tools';
})

toolsDialogClose.addEventListener("click", (e) => {
    toolsDialog.close();
})

toolsUpdate.addEventListener("click", async (e) => {
    toolsLabel.innerText = 'Updating...';
    let resp = await fetch("/tools/update", {"method": "POST"});
    toolsLabel.innerText = 'Tools';
    alert(await resp.text());
    updateToolsDialogOptions();
})

viewGenCode.addEventListener("click", (e) => {
    window.open(`https://github.com/google/ARC-GEN/blob/main/tasks/training/task${String(viewingTaskNum).padStart(3,'0')}.py`)
})

copySol.addEventListener('click', async (e) => {
    window.navigator.clipboard.writeText([...solutionView.state.doc.toString()].map(q => q.charCodeAt(0).toString(16).padStart(2, '0')).join(""));
    alert("Copied")
})


pasteSol.addEventListener('click', async (e) => {
    let inp = await window.navigator.clipboard.readText();
    if (![...inp.replaceAll(/\s/g, '')].every(q => "0123456789abcdef".includes(q))) {
        alert("not all hex!!! fail");
        return;
    }
    function hexToBytes(hex) {
        let bytes = "";
        for (let c = 0; c < hex.length; c += 2)
            bytes += (String.fromCharCode(parseInt(hex.substr(c, 2), 16)));
        return bytes;
    }
    inp = hexToBytes(inp);
    solutionView.dispatch({ changes: { from: 0, to: solutionView.state.doc.length, insert: inp } })
    ignoreWebsocketUntil = websocketTiming+0.5;
    websocketSendSolution(true);
})


let updateEverythingAccordingToViewingTaskNum = async () => {
    while (copyTestcaseButtons.firstChild) { copyTestcaseButtons.firstChild.remove(); }

    if (websocket.readyState !== WebSocket.CONNECTING) {
        annotationsView.dispatch({ changes: { from: 0, to: annotationsView.state.doc.length, insert: "" } })
        solutionView.dispatch({ changes: { from: 0, to: solutionView.state.doc.length, insert: "" } })
        websocketSendViewTask()
        openToReceiving = false;
    }
    localStorage.setItem("goog-task", viewingTaskNum)
    taskElm.value = viewingTaskNum+[];
    prevTaskVal = taskElm.value;
    receivedKnown = 0;
    resultElm.style.backgroundImage = "";
    while (resultElm.firstChild) { resultElm.firstChild.remove(); }
    previewElm.innerHTML = `<img src="/view/${viewingTaskNum}" class="max-width">`

    let resp = await fetch(`/infos/task${String(viewingTaskNum).padStart(3, '0')}.json`)
    if (resp.status == 200) {
        let info = await resp.json();
        let copiedToClipboardTimeout = undefined;
        let createTestcaseButton = (s, casefn) => {
            let elm = document.createElement("div")
            elm.classList.add("fancy-button");
            elm.innerText = s;
            elm.addEventListener("mouseover", () => {
                if (copiedToClipboardTimeout === undefined) {
                    copyTestcaseButtonsLabel.innerText = "(shift=output, ctrl=view)"
                }
            });
            elm.addEventListener("mouseout", () => {
                if (copiedToClipboardTimeout === undefined) {
                    copyTestcaseButtonsLabel.innerText = "Copy/view test case:"
                }
            })
            elm.addEventListener("click", async (e) => {
                let test = casefn();
                if (test === undefined) {
                    copyTestcaseButtonsLabel.innerText = "Failure"
                    copiedToClipboardTimeout = setTimeout(() => {
                        copiedToClipboardTimeout = undefined;
                        copyTestcaseButtonsLabel.innerText = "Copy/view test case:"
                    }, 1000)
                    return document.createTextNode("");  // empty text is nothing hack
                }
                if (e.ctrlKey) {  // viewing
                    copyTestcaseButtonsLabel.innerText = "Rendering ..."

                    resultElm.style.backgroundImage = "";
                    while (resultElm.firstChild) { resultElm.firstChild.remove(); }

                    let loadingElm = document.createElement("code");
                    loadingElm.innerHTML = "<br>rendering ...";
                    resultElm.appendChild(loadingElm)

                    let resp = await fetch(`/viewtc/${viewingTaskNum}/${test.n}`)
                    function _arrayBufferToBase64( buffer ) {
                        var binary = '';
                        var bytes = new Uint8Array( buffer );
                        var len = bytes.byteLength;
                        for (var i = 0; i < len; i++) {
                            binary += String.fromCharCode( bytes[ i ] );
                        }
                        return window.btoa( binary );
                    }
                    let src = 'data:image/png;base64,'+_arrayBufferToBase64(await resp.arrayBuffer());
                    console.log(src)

                    resultElm.style.backgroundImage = "";
                    while (resultElm.firstChild) { resultElm.firstChild.remove(); }

                    let rendered = document.createElement("img");
                    rendered.src = src;
                    rendered.classList.add("broken");
                    resultElm.appendChild(rendered)

                    copyTestcaseButtonsLabel.innerText = "Copy/view test case:"
                    return;
                }
                try {
                    let arr = e.shiftKey ? test.output : test.input;
                    navigator.clipboard.writeText(JSON.stringify(arr).replaceAll(",", ', ').replaceAll('], [','],\n['))
                } catch (e) { alert(String(e)) }
                copyTestcaseButtonsLabel.innerText = "Copied!"
                copiedToClipboardTimeout = setTimeout(() => {
                    copiedToClipboardTimeout = undefined;
                    copyTestcaseButtonsLabel.innerText = "Copy/view test case:"
                }, 1000)
            })
            return elm;
        }
        let tests = info.train.concat(info.test);
        let allTests = tests.concat(info['arc-gen'])
        while (copyTestcaseButtons.firstChild) { copyTestcaseButtons.firstChild.remove(); }
        for (let i=0; i<tests.length; i++) {
            copyTestcaseButtons.appendChild(createTestcaseButton(String(i+1), () => {
                tests[i].n = i+1;
                return tests[i];
            }))
        }
        copyTestcaseButtons.appendChild(createTestcaseButton("N", () => {
            let n=parseInt((prompt("N=?") ?? "X").replaceAll(/[^0-9]/g, ''));
            if (isNaN(n) || !isFinite(n) || n > allTests.length || n < 1) {
                return;
            }
            allTests[n-1].n = n;
            return allTests[n-1];
        }))
        copyTestcaseButtons.appendChild(createTestcaseButton("Random", () => {
            let n=Math.floor(Math.random()*allTests.length);
            alert(`Using test ${n+1}`)
            allTests[n].n = n+1;
            return allTests[n];
        }))
    }
}

let runTask = async () => {
    resultElm.style.backgroundImage = "";
    while (resultElm.firstChild) { resultElm.firstChild.remove(); }

    let loadingElm = document.createElement("code");
    loadingElm.innerHTML = "<br>loading ...";
    resultElm.appendChild(loadingElm)

    let resp = await fetch(`/run/${viewingTaskNum}`, {
        method: "POST", body: [...solutionView.state.doc.toString()].map(c => c.charCodeAt(0).toString(16).padStart(2, '0')).join(""),
        headers: {"x-long-timeout": longTimeout.checked}
    })
    let text = await resp.text();

    while (resultElm.firstChild) { resultElm.firstChild.remove(); }

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
    websocketSendRandomUnsolvedRequest();
})

randomNegative.addEventListener('click', async (e) => {
    websocketSendRandomNegativeRequest();
})

downloadZip.addEventListener('click', async (e) => {
    websocketSendDownloadZipRequest();
})


let prevTaskVal;
let lastNonEmptyTaskVal;
taskElm.addEventListener("keydown", (e) => {
    setTimeout(() => {
        if (prevTaskVal === taskElm.value) {
            return;  // avoid flicker
        }
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

        prevTaskVal = taskElm.value;
    }, 3)
})
taskElm.addEventListener("blur", () => {
    if (taskElm.value === "") {
        taskElm.value = Math.floor(lastNonEmptyTaskVal*1);
    }
})
setInterval(() => {
    if (taskElm.value !== "") {
        lastNonEmptyTaskVal=taskElm.value;
    }
}, 10)

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

setInterval(() => {
    try {
        let solstart = solutionView.state.selection.ranges[0].from ?? 0;
        let solend = solutionView.state.selection.ranges[0].to ?? 0;
        let annostart = annotationsView.state.selection.ranges[0].from ?? 0;
        let annoend = annotationsView.state.selection.ranges[0].to ?? 0;
        if (Math.abs(solend-solstart) > 0 || Math.abs(annoend-annostart) > 0) {
            if (Math.abs(solend-solstart) > 0) {
                charCount.innerText = Math.abs(solend-solstart) + " bytes"
            } else {
                charCount.innerText = Math.abs(annoend-annostart) + " bytes"
            }
        } else {
            charCount.innerText = solutionView.state.doc.toString().length + " bytes"
        }
        knownCount.innerText = receivedKnown + " bytes"
        charCount.classList.remove("char-count-bad")
        charCount.classList.remove("char-count-good")
        let ours = solutionView.state.doc.toString().length;
        let theirs = receivedKnown;
        if (ours !== 2500 && theirs !== 2500 && ours !== 0 && theirs !== 0) {
            charCount.classList.add(ours > theirs ? 'char-count-bad' : 'char-count-good')
        }
    } catch (e) { console.log(e) }
}, 50)

setInterval(() => {
    if (websocketTiming == -1) { return; }
    if (Math.abs(websocketTiming - Date.now()/1000) < 3) { return; }
    if (!refreshAsapMessageGiven) {
        refreshAsapMessageGiven = true;
        alert("No packet in 3 seconds! You could be disconnected. Please copy your sol/annotations to clipboard and refresh ASAP!");
        setInterval(() => {
            alert("No packet in 3 seconds! You could be disconnected. Please copy your sol/annotations to clipboard and refresh ASAP!");
        }, 30000)
    }
}, 500);

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
updateToolsDialogOptions()
