import { $el } from "../../../scripts/ui.js";


function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = window.crypto.getRandomValues(new Uint8Array(1))[0] % 16 | (c === 'x' ? 0 : 8);
        return r.toString(16);
    });
}
let dialogStack = [];
export function drawer(params) {
    const id = `bizyair-drawer${generateUUID()}`;
    let position = { left: 0 }
    const r = params.direction && params.direction === 'right'
    if (r) {
        position = {
            right: 0
        }
    }
    console.log(position)
    const el = $el("div.bizyair-drawer", {
        parent: document.body,
        id,
        style: {
            zIndex: 10000 + document.querySelectorAll('.bizyair-drawer').length,
            ...position
         },
        onclick: function () {
            if (params.closeOnClickModal) {
                removeDialog(this)
            }
        },
    }, [
        $el("div.bizyair-drawer-content", {
            onclick: (e) => {
                e.stopPropagation();
            }
        }, [
            (params.title ? $el("p.bizyair-drawer-title", {}, [params.title]) : ''),
            $el("span.bizyair-icon-operate.bizyair-icon-close", {
                onclick: () => {
                    removeDialog(el)
                }
            }),
            params.content
        ])
    ]);
    const fnEscapeClose = async (e) => {
        if (e.key === "Escape") {
            const topDialog = dialogStack[dialogStack.length - 1];

            if (topDialog === el) {
                if (params.onNo) {
                    await params.onNo();
                }
                removeDialog(el);
            }
        }
    };
    dialogStack.push(el);

    if (!params.onEscape) {
        document.addEventListener("keydown", fnEscapeClose);
    }

    function removeDialog(el) {
        requestAnimationFrame(() => {
            el.querySelector('.bizyair-drawer-content').style.transition = 'all 0.2s';
            // el.querySelector('.bizyair-drawer-content').style.transform = 'scale(0)';
            if (r) {
                el.querySelector('.bizyair-drawer-content').style.left = '-100%';
            } else {
                el.querySelector('.bizyair-drawer-content').style.right = '-100%';
            }
            el.style.transition = 'all 0.3s';
            el.style.opacity = '0';
            setTimeout(() => {
                el.remove();
            }, 200);
        });
        document.removeEventListener("keydown", fnEscapeClose);
        dialogStack = dialogStack.filter(d => d !== el);
    }
}
