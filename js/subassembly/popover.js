import { $el } from "../../../scripts/ui.js";

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = window.crypto.getRandomValues(new Uint8Array(1))[0] % 16 | (c === 'x' ? 0 : 8);
        return r.toString(16);
    });
}

export function popover(params) {
    const preset = {
        slots: $el('button'),
        content: '',
        onclose: () => {},
        trigger: 'hover',
        'popper-class': '',
    }
    params = params || {};
    for (const i in preset) {
        if (!params[i]) {
            params[i] = preset[i]
        }
    }
    const id = `bizyair-popover${generateUUID()}`;
    let iTimer = null

    let trigger = {
        onmouseover: () => {
            clearTimeout(iTimer)
            creatContent()
        },
        onmouseout: () => {
            removeContent()
        }
    }
    if (trigger.params === 'click') {
        trigger = {
            onclick: () => {
                creatContent()
            }
        };
        document.addEventListener('click', () => {
            for (const e of document.querySelectorAll('.bizyair-popover-content')) {
                e.remove()
            }
        })
    }
    const creatContent = () => {
        if (document.querySelector(`#${id}`)) return
        const clientRect = el.getBoundingClientRect()
        const style = {
            top: `${clientRect.y + clientRect.height}px`,
            zIndex: 10000 + document.querySelectorAll('.bizyair-popover').length,
        }
        const l = params.direction && params.direction === 'left'
        if (l) {
            style.left = `${clientRect.x}px`
        } else {
            style.right = `${document.body.clientWidth - (clientRect.x + clientRect.width)}px`
        }
        $el('div.bizyair-popover-content', {
            parent: document.body,
            id,
            style,
            ...trigger
        }, [
            params.content
        ])
    }
    const removeContent = () => {
        iTimer = setTimeout(() => {
            document.querySelector(`#${id}`).remove()
            params.onclose()
        }, 300)
    }
    const el = $el("div.bizyair-popover", {
        parent: document.body,
        ...trigger,
    }, [
        params.slots
    ]);
    return Object.assign(el, {
        close: () => {
            removeContent();
            return el;
        }
    });
}
