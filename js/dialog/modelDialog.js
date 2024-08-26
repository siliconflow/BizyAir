// import { app } from "../../../scripts/app.js";
import { $el, ComfyDialog } from "../../../scripts/ui.js";
// import { ConfirmDialog } from "../subassembly/confirm.js";
import { modelList } from "./modelList.js";
import { uploadPage } from "./uploadFile.js";
export class ModelDialog extends ComfyDialog {
    constructor(listData, typeData) {
        super();
        const __this = this
        let modelListData = listData
        let typeListData = typeData
        
        const initUpload = uploadPage(typeListData)
        const close_button = $el("button.comfy-bizyair-close", { 
            type: "button", 
            textContent: "Close", 
            onclick: () => this.close() 
        });
        const submit_button = $el("button.comfy-bizyair-submit", { 
            type: "button", 
            textContent: "submit", 
            style: { display: 'none' },
            onclick: () => initUpload.toSubmit() 
        });
        const handleTabItemClass = (ele) => {
            const tabItem = document.querySelectorAll('.bizyair-header-tab-item');
            tabItem.forEach(e => {
                e.className = 'bizyair-header-tab-item'
            })
            ele.className = 'bizyair-header-tab-item bizyair-header-tab-item-active'
        }
        const content =
            $el("div.comfy-modal-content",
                [
                    $el("div.bizyair-header-tab", {}, [
                        $el('div.bizyair-header-tab-item.bizyair-header-tab-item-active', {
                            onclick: function() {
                                __this.showModel()
                                handleTabItemClass(this)
                                submit_button.style.display = 'none'
                            }
                        }, ['uoplod list']),
                        $el('div.bizyair-header-tab-item', {
                            onclick: function() {
                                __this.showUpload()
                                handleTabItemClass(this)
                                submit_button.style.display = 'block'
                            }
                        }, ['uoplod model'])
                    ]),
                    $el('div.bizyair-d-content-item', { 
                        id: 'bizyair-d-model',
                        style: { display: 'block' }
                    }, [ modelList(modelListData) ]),
                    $el('div.bizyair-d-content-item', { 
                        id: 'bizyair-d-upload',
                        style: { display: 'none' }
                    }, [ initUpload.content ]),
                    $el('div.cm-bottom-footer', {}, [close_button, submit_button]),
                ]
            );
        this.element = $el("div.comfy-modal.bizyair-dialog", { parent: document.body }, [content]);
        
    }
    showModel() {
        document.querySelector('#bizyair-d-model').style.display = 'block'
        document.querySelector('#bizyair-d-upload').style.display = 'none'
        
    }
    showUpload() {
        document.querySelector('#bizyair-d-model').style.display = 'none'
        document.querySelector('#bizyair-d-upload').style.display = 'block'
    }
    showDialog(listData, typeData) {
        this.element.style.display = "block";
        this.modelListData = listData
        this.typeListData = typeData
    }
}