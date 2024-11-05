import { dialog } from '../subassembly/dialog.js';
import { $el } from "../../../scripts/ui.js";
import { openOAuthPopup } from "./oauth.js";
import { notifySubscribers } from "../subassembly/subscribers.js";
import { toast } from '../subassembly/toast.js';

export function apiKey() {
    async function toSubmit() {
        const apiKey = document.querySelector('#bizyair-api-key');
        if (!apiKey.value) {
            dialog({
                content: "Please input API Key",
                noText: 'Close',
                type: 'error',
            });
            apiKey.className = `${apiKey.className} cm-input-item-error`
            return false

        }
        const response = await fetch('/bizyair/set_api_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `api_key=${encodeURIComponent(apiKey.value)}`
        });
        if (response.ok) {
            // alert('API Key set successfully!');
            toast({
                content: 'API Key set successfully!',
                type: 'succeed',
                center: true
            })
            setCookie('api_key', apiKey.value, 30);
            notifySubscribers('loginRefresh', apiKey.value)
        } else {
            // alert(`Failed to set API Key: ${await response.text()}`);
            toast({
                content: `Failed to set API Key: ${await response.text()}`,
                type: 'error',
                center: true
            })
        }
        return response
    }
    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = `; expires=${date.toUTCString()}`;
        }
        document.cookie = `${name}=${value || ""}${expires}; path=/`;
    }
    const content =
        $el("div.comfy-modal-content-sml",
            [
                $el('input.cm-input-item', {
                    id: 'bizyair-api-key',
                    type: 'password',
                    placeholder: 'API Key',
                    onchange: function() {
                        this.className = 'cm-input-item'
                    }
                }),
                $el('p.confirm-word', {}, [
                    'Please',
                    $el('span.bizyair-link', {
                        onclick: () => {
                            openOAuthPopup((key) => {
                                document.querySelector('#bizyair-api-key').value = key;
                                requestAnimationFrame(() => {
                                    toSubmit().then(removeDialog)
                                });
                            });
                        }
                    }, ['click to login']),
                    "and autofill the key,"
                ]),
                $el('p.confirm-word', {}, ['or visit', $el('a.bizyair-link', { href: 'https://cloud.siliconflow.cn', target: '_blank' }, ['https://cloud.siliconflow.cn']), "to get your key and input manually."]),
                $el('p.confirm-word', {}, [
                    "Setting the API Key signifies agreement to the",
                    $el('a.bizyair-link', {
                        href: 'https://docs.siliconflow.cn/docs/user-agreement',
                        target: '_blank'
                    }, ['User Agreement']),
                    "and",
                    $el('a.bizyair-link', {
                        href: 'https://docs.siliconflow.cn/docs/privacy-policy',
                        target: '_blank'
                    }, ['Privacy Policy.']),
                ])
            ]
        );
    const removeDialog = dialog({
        title: 'Set API Key',
        content: content,
        yesText: 'Submit',
        noText: 'Close',
        onYes: toSubmit
    });
}
