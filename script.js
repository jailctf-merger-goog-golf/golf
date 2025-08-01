import {EditorView, basicSetup} from "codemirror"
import {python} from "@codemirror/lang-python"
import {oneDark} from "@codemirror/theme-one-dark"


let resultElm = document.getElementById("result");
let taskElm = document.getElementById("task");
let previewElm = document.getElementById("preview");
let leftButton = document.getElementById("left");
let rightButton = document.getElementById("right");
let runButton = document.getElementById("run");

taskElm.value = localStorage.getItem("goog-task") ?? "1"

let updateUIWithTask = async (taskNum) => {
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

    if (!text.includes("code IS READY for submission")) {
        let imgsDiv = document.createElement('div')
        imgsDiv.classList.add('flex-horizontal')

        let expected = document.createElement("img")
        expected.setAttribute("src", "/working/expected.png")
        expected.classList.add("broken")
        imgsDiv.appendChild(expected);

        let actual = document.createElement("img")
        actual.setAttribute("src", "/working/actual.png")
        actual.classList.add("broken")
        imgsDiv.appendChild(actual);

        resultElm.appendChild(imgsDiv);
    }

    let newElm = document.createElement("code")
    newElm.innerText = text;
    resultElm.appendChild(newElm);
    return;
}

runButton.addEventListener("click", (e) => {
    runTask(taskElm.value*1)
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

const view = new EditorView({
  parent: document.getElementById("editor"),
  doc: "",
  extensions: [basicSetup, python(), oneDark],
  lineWrapping: true,
})

window.view = view;

updateUIWithTask(localStorage.getItem("goog-task"))
