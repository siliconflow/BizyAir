import { app } from "../../scripts/app.js";
import { $el } from "../../scripts/ui.js";
import { styleMenus } from "./subassembly/styleMenus.js";
import './bizyair_frontend.js'
class FloatingButton {
    constructor(show_cases) {
        this.show_cases = show_cases
        this.button = $el("div.comfy-floating-button", {
            parent: document.body,
            style: { top: app.menu.element.style.display === 'none' ? '': '60px' },
            onmousedown: (e) => this.startDrag(e),
            id: 'bizyair-menu-item',
        }, [
            // $el("h2.bizyair-logo"),
            // $el("div.bizyair-menu", {}, [
            //     $el('strong', {}, ['BizyAir']),
            //     $el("div.bizyair-menu-item", {
            //         id: 'bizyair-menu-item',
            //     }),
            // ]),
            // $el('div.cmfy-floating-button-closer', {
            //     onclick: () => this.toggleVisibility(event)
            // })
        ]);

        bizyAirLib.mount('#bizyair-menu-item', app)


        this.dragging = false;
        this.visible = true;

        document.addEventListener("mousemove", (e) => this.doDrag(e));
        document.addEventListener("mouseup", () => this.endDrag());

    }

    getDisplayStyle(element) {
        return element.currentStyle ? element.currentStyle.display : window.getComputedStyle(element).display;
    }

    startDrag(e) {
        document.body.style.userSelect = 'none';
        this.dragging = true;
        this.offsetX = e.clientX - this.button.offsetLeft;
        this.offsetY = e.clientY - this.button.offsetTop;
        e.preventDefault();
    }

    endDrag() {
        document.body.style.userSelect = '';
        this.dragging = false;
    }

    doDrag(e) {

        if (this.dragging) {
            this.button.style.left = `${e.clientX - this.offsetX}px`;
            this.button.style.top = `${e.clientY - this.offsetY}px`;
            this.button.style.bottom = 'auto';
            this.button.style.right = 'auto';
        }
    }

    toggleVisibility(e) {
        e.stopPropagation();
        const comfyFloatingButton = document.querySelector('.comfy-floating-button')
        const bizyairMenu = document.querySelector('.bizyair-menu')
        const bizyairMenuCloser = document.querySelector('.cmfy-floating-button-closer')
        if (this.visible) {
            comfyFloatingButton.className = 'comfy-floating-button comfy-floating-button-hidden';
            bizyairMenu.className = 'bizyair-menu bizyair-menu-hidden';
            bizyairMenuCloser.className = 'cmfy-floating-button-closer cmfy-floating-button-closer-overturn'
        } else {
            comfyFloatingButton.className = 'comfy-floating-button';
            bizyairMenu.className = 'bizyair-menu';
            bizyairMenuCloser.className = 'cmfy-floating-button-closer'
        }
        this.visible = !this.visible;
    }
}

app.registerExtension({
    name: "comfy.FloatingButton",
    async setup() {
        $el("style", {
            textContent: styleMenus,
            parent: document.head,
        });
        new FloatingButton();
    },
});
