import { $el, ComfyDialog } from "../../../scripts/ui.js";
import { ConfirmDialog } from "../subassembly/confirm.js";

export class ApiKey extends ComfyDialog {
    constructor() {
        super();

        const close_button = $el("button.comfy-bizyair-close", {
            type: "button",
            textContent: "Close",
            onclick: () => this.remove()
        });
        const submit_button = $el("button.comfy-bizyair-submit", {
            type: "button",
            textContent: "Submit",
            onclick: () => this.toSubmit()
        });
        const content =
            $el("div.comfy-modal-content",
                [
                    $el("p", {}, [
                        $el("font", { size: 6, color: "white" }, [`Set API Key`]),]
                    ),
                    $el("br", {}, []),
                    $el("br", {}, []),
                    $el('input.cm-input-item', {
                        id: 'bizyair-api-key',
                        type: 'password',
                        placeholder: 'API Key',
                        onchange: function() {
                            this.className = 'cm-input-item'
                        }
                    }),
                    $el('p.confirm-word', {}, ['To get your key, visit', $el('a.bizyair-link', { href: 'https://bizyair.com', target: '_blank' }, ['https://bizyair.com'])]),
                    $el('div.cm-bottom-footer', {}, [close_button, submit_button]),
                ]
            );
        // this.element =;
        this.element = $el('div.bizyair-modal', {
            parent: document.body
        }, [
            $el("div.comfy-modal.bizyair-dialog.bizyair-dialog-sml", {
                id: 'bizyair-api-key-dialog',
                parent: document.body,
                style: { display: 'block' }
            }, [content])
        ])
    }
    async toSubmit() {
        const apiKey = document.querySelector('#bizyair-api-key');
        console.log(apiKey.value)
        if (!apiKey.value) {
            new ConfirmDialog({
                title: "",
                warning: true,
                message: "Please input API Key",
            })
            apiKey.className = `${apiKey.className} cm-input-item-error`
            return

        }
        const response = await fetch('/bizyair/set_api_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `api_key=${encodeURIComponent(apiKey.value)}`
        });
        if (response.ok) {
            alert('API Key set successfully!');
            this.setCookie('api_key', apiKey.value, 30);
            this.close();
        } else {
            alert('Failed to set API Key: ' + await response.text());
        }
    }
    setCookie(name, value, days) {
        var expires = "";
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }
    remove() {
        this.element.remove();
    }
    showDialog() {
        this.element.style.display = "block";
    }
}
