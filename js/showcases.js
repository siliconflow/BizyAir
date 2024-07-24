import { api } from "../../../../scripts/api.js";
import { app } from "../../../scripts/app.js";
import { $el } from "../../../scripts/ui.js";

const style = `
#comfy-floating-button {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: auto;
    height: 50px;
    border-radius: 10px;
    background-color: rgb(130, 88, 245);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25);
    user-select: none;
    padding: 0 15px;
    white-space: nowrap;
}

#comfy-floating-button:hover {
    background-color: rgb(100, 68, 215);
}

.comfy-floating-menu .context-menu-item {
    position: relative;
}

.comfy-floating-menu .context-menu-item .summary {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    background: white;
    color: black;
    padding: 5px;
    border: 1px solid #ccc;
    border-radius: 5px;
    white-space: nowrap;
    z-index: 1000;
}

.comfy-floating-menu .context-menu-item:hover .summary {
    display: block;
}
`;

class FloatingButton {
    constructor(show_cases) {
        this.show_cases = show_cases
        this.button = $el("div", {
            id: "comfy-floating-button",
            textContent: "☁️BizyAir Workflow Examples ➕",
            onmousedown: (e) => this.startDrag(e),
            onclick: (e) => this.showMenu(e),
        });
        document.body.appendChild(this.button);
        this.dragging = false;

        document.addEventListener("mousemove", (e) => this.doDrag(e));
        document.addEventListener("mouseup", () => this.endDrag());
    }

    async showMenu(e) {
        if (this.dragging) return; // Prevent showing menu during drag
        e.preventDefault();
        e.stopPropagation();

        LiteGraph.closeAllContextMenus();
        const menu = new LiteGraph.ContextMenu(
            await this.getMenuOptions(),
            {
                event: e,
                scale: 1.3,
            },
            window
        );
        menu.root.classList.add("comfy-floating-menu");
    }

    async get_workflow_graph(file) {
        console.log("workflow file:", file);
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

    async getMenuOptions() {
        return this.show_cases.map(item => ({
            title: item.title,
            callback: async () => await this.get_workflow_graph(item.file),
        }));
    }

    startDrag(e) {
        this.dragging = true;
        this.offsetX = e.clientX - this.button.offsetLeft;
        this.offsetY = e.clientY - this.button.offsetTop;
    }

    endDrag() {
        this.dragging = false;
    }

    doDrag(e) {
        if (this.dragging) {
            this.button.style.left = (e.clientX - this.offsetX) + 'px';
            this.button.style.top = (e.clientY - this.offsetY) + 'px';
            this.button.style.bottom = 'auto';
            this.button.style.right = 'auto';
        }
    }
}

app.registerExtension({
    name: "comfy.FloatingButton",
    async setup() {
        $el("style", {
            textContent: style,
            parent: document.head,
        });
        const response = await api.fetchApi("/bizyair/showcases",
            { method: "GET" });
        if (response.status === 200) {
            const show_cases = await response.json()
            new FloatingButton(show_cases);
        } else {
            console.log("error occurs when fetch the showcases:", await response.text())
        }
    },
});
