import { app } from "../../scripts/app.js";
import { $el } from "../../scripts/ui.js";
import { exampleBtn } from "./itemButton/btnExample.js";
import { apiKeyBtn } from "./itemButton/btnApiKey.js";
import { myInfoBtn } from "./itemButton/myInfo.js";
import { modelBtn } from "./itemButton/btnModel.js";
import { newsBtn } from "./itemButton/btnNews.js";
import { styleExample } from "./subassembly/styleExample.js";
import { styleMenus } from "./subassembly/styleMenus.js";
import { styleUploadFile } from "./subassembly/styleUploadFile.js";
import { styleDialog } from './subassembly/styleDialog.js';
import { styleMyInfo } from './subassembly/styleMyInfo.js';
import { notifySubscribers, subscribe } from './subassembly/subscribers.js'
import { WebSocketClient } from './subassembly/socket.js'
import { toast } from './subassembly/toast.js'
import { getUserInfo } from './apis.js'

let userMenu = apiKeyBtn

class FloatingButton {
    constructor(show_cases) {
        this.show_cases = show_cases
        this.button = $el("div.comfy-floating-button", {
            parent: document.body,
            style: { top: app.menu.element.style.display === 'none' ? '': '60px' },
            onmousedown: (e) => this.startDrag(e),
        }, [
            $el("h2.bizyair-logo"),
            $el("div.bizyair-menu", {}, [
                $el('strong', {}, ['BizyAir']),
                $el("div.bizyair-menu-item", {}, [
                    exampleBtn,
                    userMenu,
                    modelBtn,
                    newsBtn,
                ]),
            ]),
            $el('div.cmfy-floating-button-closer', {
                onclick: () => this.toggleVisibility(event)
            })
        ]);

        this.dragging = false;
        this.visible = true;

        document.addEventListener("mousemove", (e) => this.doDrag(e));
        document.addEventListener("mouseup", () => this.endDrag());

    }

    getDisplayStyle(element) {
        return element.currentStyle ? element.currentStyle.display : window.getComputedStyle(element).display;
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
        $el("style", {
            textContent: styleExample,
            parent: document.head,
        });
        $el("style", {
            textContent: styleUploadFile,
            parent: document.head,
        });
        $el("style", {
            textContent: styleDialog,
            parent: document.head,
        });
        $el("style", {
            textContent: styleMyInfo,
            parent: document.head,
        });
        getUserInfo().then(info => {
            sessionStorage.setItem('userInfo', JSON.stringify(info.data))
            userMenu = info?.data ? myInfoBtn() : apiKeyBtn
            new FloatingButton();
        }).catch(() => {
            new FloatingButton();
        })

        const wsClient = new WebSocketClient(`ws://${location.host}/bizyair/modelhost/ws?clientId=${sessionStorage.getItem('clientId')}`);
        wsClient.onMessage = message => {
            notifySubscribers('socketMessage', message);
            const res = JSON.parse(message.data);
            if (res && res.type === 'errors') {
                toast.error(res.data.message)
            }
        }
        subscribe('loginRefresh', () => {
            document.querySelector('.comfy-floating-button').remove()
            getUserInfo().then(info => {
                sessionStorage.setItem('userInfo', JSON.stringify(info.data))
                userMenu = info?.data ? myInfoBtn() : apiKeyBtn
                new FloatingButton();
            }).catch(() => {
                new FloatingButton();
            })
        })
    },
});
