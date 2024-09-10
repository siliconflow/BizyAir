import { $el } from "../../../scripts/ui.js";

let keydownListenerAdded = false;

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = window.crypto.getRandomValues(new Uint8Array(1))[0] % 16 | (c === 'x' ? 0 : 8);
        return r.toString(16);
    });
}
function removeDialog(el) {
    el.querySelector('.bizyair-dialog-content').style.transition = 'all 0.2s';
    el.querySelector('.bizyair-dialog-content').style.transform = 'translate(-50%, -50%) scale(0)';
    el.style.transition = 'all 0.3s';
    el.style.opacity = '0';
    setTimeout(() => {
        el.remove();
    }, 200);
}
export function dialog(params) {
    const id = 'bizyair-dialog' + generateUUID();
    const style = {}
    let h = 'calc(80vh - 40px - 40px)';
    if (params.yesText || params.noText) {
        h = 'calc(80vh - 40px - 40px - 34px)'
    }
    if (params.title) {
        h = 'calc(80vh - 40px - 40px - 34px - 48px)'
    }
    function setContent() {
        if (params.content) {
            return $el("div.bizyair-new-dialog-body", {
                style: { maxHeight: h }
            }, [
                (params.succeed? $el('div.bizyair-new-dialog-icon.bizyair-new-dialog-succeed', {}, []): ''),
                (params.warning? $el('div.bizyair-new-dialog-icon.bizyair-new-dialog-warning', {}, []): ''),
                (params.error? $el('div.bizyair-new-dialog-icon.bizyair-new-dialog-error', {}, []): ''),
                params.content
            ])
        }
        return ''
    }
    $el("div.bizyair-new-dialog", {
        parent: document.body,
        id,
        style: { zIndex: 1000 + document.querySelectorAll('.bizyair-new-dialog').length },
        onclick: function () {
            if (params.closeOnClickModal) {
                removeDialog(this)
            }
        },
    }, [
        $el("div.bizyair-dialog-content", {
            style,
            onclick: function (e) {
                e.stopPropagation();
            }
        }, [
            (params.title ? $el("p.bizyair-new-dialog-title", { }, [params.title]) : ''),
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
                        removeDialog(document.getElementById(id))
                    }
                }): ''),
                (params.noText ? $el("button.bizyair-new-dialog-btn", {
                    type: "button",
                    textContent: params.noText,
                    onclick: async () => {
                        if (params.onNo) {
                            await params.onNo();
                        }
                        removeDialog(document.getElementById(id))
                    }
                }): '')
                
            ]),
        ])
    ]);

    if (!params.onEsape && !keydownListenerAdded) {
        document.addEventListener("keydown", function (e) {
            console.log(e.key, document.querySelectorAll('.bizyair-new-dialog').length);
            if (e.key === "Escape") {
                const dialogs = document.querySelectorAll('.bizyair-new-dialog');
                if (dialogs.length > 0) {
                    removeDialog(dialogs[dialogs.length - 1])
                }
            }
        });
        keydownListenerAdded = true;
    }
}

// dialog({
//     title: 'Title',
//     content: 'asdasd',
//     noText: 'Close',
//     error: true
// });