import {EditorView, basicSetup} from "codemirror"
import {python} from "@codemirror/lang-python"
import {oneDark} from "@codemirror/theme-one-dark"


let resultElm = document.getElementById("result");
let taskElm = document.getElementById("task");
let previewElm = document.getElementById("preview");
let leftButton = document.getElementById("left");
let rightButton = document.getElementById("right");
let runButton = document.getElementById("run");
let uploadButton = document.getElementById("upload-solution");
let gitpullButton = document.getElementById("do-git-pull");

taskElm.value = localStorage.getItem("goog-task") ?? "1"

let updateUIWithTask = async (taskNum) => {
    resultElm.style.backgroundImage = "";
    uploadButton.disabled = true; // dont upload until we get a valid submission
    while (resultElm.firstChild) {
        resultElm.firstChild.remove();
    }
    previewElm.innerHTML = `<img src="/view/${taskNum}" class="max-width">`
    try {
        let resp = await fetch(`/sols/${taskNum}`)
        let text;
        if (resp.status == 404) {
            text = ""
        } else {
            text = await resp.text();
        }
        view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: text } })
    } catch (e) {
        alert(e)
    }
}

let runTask = async (taskNum) => {
    resultElm.style.backgroundImage = "";
    if (taskNum == undefined) {
        alert("massive error contact quasar098");
        return
    }
    while (resultElm.firstChild) {
        resultElm.firstChild.remove();
    }
    let resp = await fetch(`/run/${taskNum}`, {method: "POST", body: view.state.doc.toString()})
    let text = await resp.text();
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
        expected.setAttribute("src", "/working/expected.png?" + Date.now())
        expected.classList.add("broken")
        imgsDiv.appendChild(expected);

        let actual = document.createElement("img")
        actual.setAttribute("src", "/working/actual.png?" + Date.now())
        actual.classList.add("broken")
        imgsDiv.appendChild(actual);

        resultElm.appendChild(imgsDiv);
    }
    if (text.includes("code IS READY for submission")) {
        resultElm.style.backgroundImage = "url(https://i.etsystatic.com/28810262/r/il/2fc5e0/5785166966/il_fullxfull.5785166966_nvy4.jpg)"
        uploadButton.disabled = false; // good solution, can upload now
    }

    let newElm = document.createElement("code")
    newElm.innerText = text;
    resultElm.appendChild(newElm);
    return;
}

runButton.addEventListener("click", (e) => {
    runTask(taskElm.value*1)
})

let doGitPull = async () => {
    let resp = await fetch(`/actions/pull`, {method: "POST"});
    let text = await resp.text();
    if (resp.status == 500) {
        // returncode was nonzero
        console.log("Git Pull Failed! Message:");
        console.log(text);
        console.log("=".repeat(30));
        alert("Git Pull failed. Check console for details.");
        return;
    }

    if (resp.status == 501 || resp.status == 200) {
        // timeout/success, just alert return message from server
        alert(text);
        return;
    }

    console.log(`Got response code ${resp.status} while doing git pull.`);
    console.log(`message: ${text}`);
    alert("Got unknown response from server, check logs.");
}

gitpullButton.addEventListener("click", (e) => {
    doGitPull();
})

let doUpload = async (taskNum) => {
    if (taskNum == undefined) {
        alert("massive error in doUpload");
        return
    }

    let resp = await fetch(`/upload/${taskNum}`, {method: "POST"})
    let text = await resp.text();

    if (resp.status != 200) {
        // can be missing file, timeout, or git cmd failing
        console.log(`Upload Failed! Message:`);
        console.log(text);
        console.log("=".repeat(30));
        alert("Upload failed, check console logs");
        return;
    }

    // yay success! just give them the message that the server returned
    alert(text);
}

uploadButton.addEventListener("click", (e) => {
    doUpload(taskElm.value*1)
})

taskElm.addEventListener("keydown", (e) => {
    setTimeout(() => {
        if (!parseInt(taskElm.value)) {
            return;
        }
        let taskNum = Math.min(Math.max((1*taskElm.value), 1), 400)
        taskElm.value = taskNum + []
        localStorage.setItem("goog-task", taskElm.value)
        updateUIWithTask(taskNum)
    }, 20)
})
leftButton.addEventListener("click", (e) => {
    let taskNum = ((1*taskElm.value) + 398) % 400 + 1
    taskElm.value = taskNum + []
    localStorage.setItem("goog-task", taskElm.value)
    updateUIWithTask(taskNum)
})
rightButton.addEventListener("click", (e) => {
    let taskNum = ((1*taskElm.value) + 400) % 400 + 1
    taskElm.value = taskNum + []
    localStorage.setItem("goog-task", taskElm.value)
    updateUIWithTask(taskNum)
})

const theme = EditorView.theme({
  "&": {
    fontSize: "12pt",
    border: "1px solid #c0c0c0"
  },
});

const view = new EditorView({
  parent: document.getElementById("editor"),
  doc: "",
  extensions: [basicSetup, python(), oneDark, [theme]],// EditorView.lineWrapping],
})

window.theme = theme;
window.view = view;

updateUIWithTask(localStorage.getItem("goog-task"))
