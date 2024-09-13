import { app } from "../../../scripts/app.js";
import { $el } from "../../../scripts/ui.js";
import { api } from "../../../scripts/api.js";

let dragging = false;
document.addEventListener("click", () => {
    const exampleMenu = document.querySelector(".example-menu")
    if (exampleMenu) document.body.removeChild(exampleMenu);
});

export async function showMenu(e, show_cases) {
    if (dragging) return;
    e.preventDefault();
    e.stopPropagation();

    const exampleMenu = document.querySelector(".example-menu")
    if (exampleMenu) document.body.removeChild(exampleMenu);
    const keys = Object.keys(show_cases)
    document.body.appendChild($el(
        "ul.example-menu",
        {
            style: {
                position: "absolute",
                top: e.clientY + "px",
                left: e.clientX + "px",
                zIndex: 1000,
            }
        },
        keys.map(item => mapHtmls(show_cases[item], item))
    ))
}

export function mapHtmls(item, key) {
    if (typeof item === 'string' || typeof item === 'function') {
        return $el("li", {
            textContent: key,
            onclick: async () => await get_workflow_graph(item)
        });
    } else {
        const keys = Object.keys(item)
        return $el("li.has-child", {
            textContent: key,
            onclick: function (e) {
                e.preventDefault();
                e.stopPropagation();
                const childList = this.querySelector(".child-list");
                this.classList.toggle('show-child');
                childList.style.display = childList.style.display === 'block' ? 'none' : 'block';
            }
        }, [
            $el("ul.child-list", { style: { display: "none" } }, keys.map(e => mapHtmls(item[e], e)))
        ])
    }
}

export async function get_workflow_graph(file) {
    if (typeof file === 'function') {
        file()
        return
    }
    if (file.startsWith("https://")) {
        console.log("open BizyAir NEWS:", file);
        window.open(file, '_blank');
    } else if (file.endsWith(".json")) {
        console.log("workflow file:", file);
        const exampleMenu = document.querySelector(".example-menu")
        if (exampleMenu) document.body.removeChild(exampleMenu);
        const response = await api.fetchApi("/bizyair/workflow", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ file: file }),
        });
        const showcase_graph = await response.json()
        app.graph.clear()
        await app.loadGraphData(showcase_graph)
    }
}