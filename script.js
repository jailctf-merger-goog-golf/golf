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
    previewElm.innerHTML = `<p id='loading'>loading</p><img src="/view/${taskNum}" onload="document.getElementById('loading').remove()" class="max-width">`
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
    if (resp.status != 200) {
        let newElm = document.createElement("p")
        newElm.style.color = "red";
        newElm.innerText = "error! (todo print error here)";  // todo do this
        resultElm.appendChild(newElm);
        return;
    }

    let text = await resp.text();
    if (!text.includes("code IS READY for submission")) {
        let broken = document.createElement("img")
        broken.setAttribute("src", "/working/broken.png")
        broken.classList.add("max-width")
        resultElm.appendChild(broken);
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
    let taskNum = Math.min(Math.max((1*taskElm.value) - 1, 1), 400)
    taskElm.value = taskNum + []
    localStorage.setItem("goog-task", taskElm.value)
    updateUIWithTask(taskNum)
})
rightButton.addEventListener("click", (e) => {
    let taskNum = Math.min(Math.max((1*taskElm.value) + 1, 1), 400)
    taskElm.value = taskNum + []
    localStorage.setItem("goog-task", taskElm.value)
    updateUIWithTask(taskNum)
})

const view = new EditorView({
  parent: document.getElementById("editor"),
  doc: "",
  extensions: [basicSetup, python(), oneDark]
})

window.view = view;

updateUIWithTask(localStorage.getItem("goog-task"))
