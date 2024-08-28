import { $el, ComfyDialog, } from "../../../scripts/ui.js";
console.log(ComfyDialog)

export class ConfirmDialog extends ComfyDialog {
    constructor(options) {
        super();
        this.options = options;
        const close_button = $el("button.comfy-bizyair-close", { 
            type: "button", 
            textContent: options.noText || "Close", 
            onclick: () => this.closeBtnClick() 
        });
        const submit_button = $el("button.comfy-bizyair-submit", { 
            type: "button", 
            textContent: options.yesText, 
            onclick: () => this.submitBtnClick() 
        });
        const content =
            $el("div.comfy-modal-content",
                [
                    $el("p", {}, [
                        $el("font", { size: 5, color: "white" }, [options.title]),]
                    ),
                    (options.warning ? 
                        $el("p", {}, [options.message])
                        :
                        $el("p.confirm-word", {}, [options.message])
                    ),
                    $el('div.cm-bottom-footer', {}, [close_button, (options.yesText ? submit_button: '')]),
                ]
            );
        this.element = $el('div.bizyair-modal', {
            parent: document.body
        }, [
            $el("div.comfy-modal.bizyair-dialog-confirm", { parent: document.body, style: { display: 'block' } }, [content])
        ])
        this.element.style.display = "block";
    }
    closeBtnClick() {
        this.element.remove();
        if (this.options.onNo) {
            this.options.onNo();
        }
    }
    submitBtnClick() {
        if (this.options.onYes) {
            this.options.onYes();
        }
        this.element.remove();
    }
}