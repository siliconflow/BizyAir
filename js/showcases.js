import { app } from "../../../scripts/app.js";
import { $el } from "../../../scripts/ui.js";

const SHOW_CASES = [
    {
        "title": "生成照片风格的图片",
        "summary": "这是一个生成照片风格图片的示例",
        "file": "bizyair_generate_photorealistic_images_workflow.json",
    },
    {
        "title": "Kolors 文生图",
        "summary": "这是一个Kolors文生图的示例",
        "file": "bizyair_generate_photorealistic_images_workflow.json",
    },
    {
        "title": "抠除背景",
        "summary": "这是一个抠除背景的示例",
        "file": "bizyair_remove_background_workflow.json",
    },
];

const style = `
#comfy-floating-button {
    position: fixed;
    top: 20px; /* 修改为屏幕中间偏上的位置 */
    left: 50%;
    transform: translateX(-50%);
    width: auto; /* 修改为自动宽度 */
    height: 50px;
    border-radius: 10px; /* 修改为圆角矩形 */
    background-color: rgb(130, 88, 245);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25);
    user-select: none;
    padding: 0 15px; /* 添加内边距以确保文本不会太靠近边缘 */
    white-space: nowrap; /* 确保文本在一行显示 */
}

#comfy-floating-button:hover {
    background-color: rgb(100, 68, 215); /* 修改为与新的背景色风格一致 */
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
    constructor() {
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

    showMenu(e) {
        if (this.dragging) return; // Prevent showing menu during drag
        e.preventDefault();
        e.stopPropagation();

        LiteGraph.closeAllContextMenus();
        const menu = new LiteGraph.ContextMenu(
            this.getMenuOptions(),
            {
                event: e,
                scale: 1.3,
            },
            window
        );
        menu.root.classList.add("comfy-floating-menu");
    }

    getMenuOptions() {
        return SHOW_CASES.map(item => ({
            title: item.title,
            callback: () => alert(item.file),
            onmouseenter: (event) => this.showSummary(event, item.summary),
            onmouseleave: (event) => this.hideSummary(event),
        }));
    }

    showSummary(event, summary) {
        console.log("showSummary called"); // 调试信息
        const summaryElement = document.createElement("div");
        summaryElement.className = "summary";
        summaryElement.textContent = summary;
        event.target.appendChild(summaryElement);
    }

    hideSummary(event) {
        console.log("hideSummary called"); // 调试信息
        const summaryElement = event.target.querySelector(".summary");
        if (summaryElement) {
            summaryElement.remove();
        }
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
    init() {
        $el("style", {
            textContent: style,
            parent: document.head,
        });
        new FloatingButton();
    },
});
