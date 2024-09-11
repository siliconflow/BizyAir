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
        const login_button = $el("button.comfy-bizyair-login", {
            type: "button",
            textContent: "Login to autofill API Key",
            onclick: () => this.openOAuthPopup()
        });
        const content =
            $el("div.comfy-modal-content",
                [
                    $el("p", {}, [
                        $el("font", { size: 6, color: "white" }, [`Set API Key`]),]
                    ),
                    $el("br", {}, []),
                    $el("br", {}, []),
                    login_button,
                    $el("br", {}, []),
                    $el('input.cm-input-item', {
                        id: 'bizyair-api-key',
                        type: 'password',
                        placeholder: 'API Key',
                        onchange: function () {
                            this.className = 'cm-input-item'
                        }
                    }),
                    $el('p.confirm-word', {}, ['Please visit', $el('a.bizyair-link', { href: 'https://cloud.siliconflow.cn', target: '_blank' }, ['https://cloud.siliconflow.cn']), " to get your key."]),
                    $el('p.confirm-word', {}, [
                        "Setting the API Key signifies agreement to the",
                        $el('a.bizyair-link', {
                            href: 'https://docs.siliconflow.cn/docs/user-agreement',
                            target: '_blank'
                        }, ['User Agreement']),
                        " and",
                        $el('a.bizyair-link', {
                            href: 'https://docs.siliconflow.cn/docs/privacy-policy',
                            target: '_blank'
                        }, ['Privacy Policy.']),
                    ]),
                    $el('div.cm-bottom-footer', {}, [submit_button, close_button]),
                ]
            );
        this.element = $el('div.bizyair-modal', {
            parent: document.body
        }, [
            $el("div.comfy-modal.bizyair-dialog.bizyair-dialog-sml", {
                id: 'bizyair-api-key-dialog',
                parent: document.body,
                style: { display: 'block' }
            }, [content])
        ])
        document.addEventListener('keydown', (e) => this.keyDown(e));
    }
    async openOAuthPopup() {
        const clientId = 'SFaJLLq0y6CAMoyDm81aMu';
        const ACCOUNT_ENDPOINT = 'https://account.siliconflow.cn';
        const authUrl = `${ACCOUNT_ENDPOINT}/oauth?client_id=${clientId}`;

        // Open a new window for the OAuth
        const popup = window.open(authUrl, 'oauthPopup', 'width=600,height=600');
        const checkUrlChange = setInterval(async () => {
            // Check if the new window is closed
            if (popup.closed) {
                clearInterval(checkUrlChange);
                console.log('The new window was closed.');
                return;
            }
            function getCodeQuery(url) {
                try {
                    const parsedUrl = new URL(url);
                    if (parsedUrl.searchParams.has('code')) {
                        return parsedUrl.searchParams.get('code');
                    } else {
                        return undefined;
                    }
                } catch (error) {
                    console.error('Invalid URL:', error);
                    return null;
                }
            }
            // Check the current URL of the new window
            try {
                const currentUrl = popup.location.href;
                console.log('Current URL:', currentUrl);
                const code = getCodeQuery(currentUrl);
                if (code) {
                    console.log('The new window has the code query parameter.', code);
                    const response = await fetch('/bizyair/fetch_api_key', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            'code': code,
                        })
                    });
                    const res = await response.json();
                    const api_key = res.api_key;
                    console.log('AK', api_key);
                    clearInterval(checkUrlChange);
                    popup.close();
                    document.getElementById('bizyair-api-key').value = api_key;
                }
            } catch (e) {
                console.warn('Cannot access URL, likely due to cross-origin restrictions.', e);
            }
        }, 1000); // Check every second
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
    keyDown(e) {
        if (e.key === 'Escape') {
            this.remove();
        }
    }
    remove() {
        this.element.remove();
        document.removeEventListener('keydown', (e) => this.keyDown(e));
    }
    showDialog() {
        this.element.style.display = "block";
    }
}
