import { $el } from "../../../scripts/ui.js";


function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = window.crypto.getRandomValues(new Uint8Array(1))[0] % 16 | (c === 'x' ? 0 : 8);
        return r.toString(16);
    });
}
let dialogStack = [];
export function dialog(params) {
    const id = `bizyair-dialog${generateUUID()}`;
    const style = {};
    let h = 'calc(80vh - 40px - 40px)';
    if (params.yesText || params.noText || params.neutralText) {
        h = 'calc(80vh - 40px - 40px - 34px)';
    }
    if (params.title) {
        h = 'calc(80vh - 40px - 40px - 34px - 48px)'
    }
    function setContent() {
        if (params.content) {
            return $el("div.bizyair-new-dialog-body", {
                style: { maxHeight: h }
            }, [
                (params.type && params.type === 'succeed' ? $el('div.bizyair-new-dialog-icon.bizyair-new-dialog-succeed', {}, []) : ''),
                (params.type && params.type === 'warning' ? $el('div.bizyair-new-dialog-icon.bizyair-new-dialog-warning', {}, []) : ''),
                (params.type && params.type === 'error' ? $el('div.bizyair-new-dialog-icon.bizyair-new-dialog-error', {}, []) : ''),
                params.content
            ])
        }
        return ''
    }
    const el = $el("div.bizyair-new-dialog", {
        parent: document.body,
        id,
        style: { zIndex: 10000 + document.querySelectorAll('.bizyair-new-dialog').length },
        onclick: function () {
            if (params.closeOnClickModal) {
                removeDialog()
            }
        },
    }, [
        $el("div.bizyair-dialog-content", {
            style,
            onclick: (e) => {
                e.stopPropagation();
            }
        }, [
            (!params.closeOnClickModal ? $el('div.bizyair-icon-operate.bizyair-icon-nude-close.bizyair-dialog-content-close', {
                onclick: () => {
                    if (params.onNo) {
                        params.onNo();
                    }
                    removeDialog(document.getElementById(id))
                }
            }) : ''),
            (params.title ? $el("p.bizyair-new-dialog-title", {}, [params.title]) : ''),
            setContent(),
            $el('div.bizyair-new-dialog-footer', {}, [
                (params.yesText ? $el("button.bizyair-new-dialog-btn", {
                    type: "button",
                    textContent: params.yesText,
                    id: params.yesId ? params.yesId : '',
                    onclick: async () => {
                        if (params.onYes) {
                            const res = await params.onYes();
                            if (!res) {
                                return false
                            }
                        }
                        removeDialog()
                    }
                }) : ''),
                (params.neutralText ? $el("button.bizyair-new-dialog-btn", {
                    type: "button",
                    textContent: params.neutralText,
                    id: params.neutralId ? params.neutralId : '',
                    onclick: async () => {
                        if (params.onNeutral) {
                            const res = await params.onNeutral();
                            if (!res) {
                                return false
                            }
                        }
                        removeDialog()
                    }
                }) : ''),
                (params.noText ? $el("button.bizyair-new-dialog-btn", {
                    type: "button",
                    textContent: params.noText,
                    onclick: async () => {
                        if (params.onNo) {
                            await params.onNo();
                        }
                        removeDialog()
                    }
                }) : '')
            ]),
        ])
    ]);
    const fnEscapeClose = async (e) => {
        if (e.key === "Escape") {
            const topDialog = dialogStack[dialogStack.length - 1];

            if (topDialog === el) {
                if (params.onNo) {
                    await params.onNo();
                }
                removeDialog();
            }
        }
    };
    dialogStack.push(el);

    if (!params.onEscape) {
        document.addEventListener("keydown", fnEscapeClose);
    }

    function removeDialog() {
        const el = document.getElementById(id);
        requestAnimationFrame(() => {
            el.querySelector('.bizyair-dialog-content').style.transition = 'all 0.2s';
            el.querySelector('.bizyair-dialog-content').style.transform = 'translate(-50%, -50%) scale(0)';
            el.style.transition = 'all 0.3s';
            el.style.opacity = '0';
            setTimeout(() => {
                el.remove();
                if (params.onClose) {
                    params.onClose();
                }
            }, 200);
        });
        document.removeEventListener("keydown", fnEscapeClose);
        dialogStack = dialogStack.filter(d => d !== el);
    }
    return {
        close: () => {
            removeDialog(document.getElementById(id))
        }
    }
}
dialog.succeed = params => {
    if (typeof params === 'string') {
        const contentParams = { content: params, type: 'succeed' }
        dialog(contentParams)
    }
    params.type = 'succeed';
    dialog(params)
}
dialog.warning = params => {
    if (typeof params === 'string') {
        const contentParams = { content: params, type: 'warning' }
        dialog(contentParams)
    }
    params.type = 'warning';
    dialog(params)
}
dialog.error = params => {
    if (typeof params === 'string') {
        const contentParams = { content: params, type: 'error' }
        dialog(contentParams)
    }
    params.type = 'error';
    dialog(params)
}
