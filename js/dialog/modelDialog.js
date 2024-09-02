// import { app } from "../../../scripts/app.js";
import { $el, ComfyDialog } from "../../../scripts/ui.js";
// import { ConfirmDialog } from "../subassembly/confirm.js";
import { modelList } from "./modelList.js";
import { uploadPage } from "./uploadFile.js";
import { models_files } from "../apis.js"


export class ModelDialog extends ComfyDialog {
    constructor(listData, typeData) {
        super();
        const __this = this
        let modelListData = listData
        let typeListData = typeData
        this.typeListData = typeListData

        const close_button = $el("button.comfy-bizyair-close", {
            type: "button",
            textContent: "Close",
            onclick: () => this.remove()
        });
        const submit_button = $el("button.comfy-bizyair-submit", {
            type: "button",
            textContent: "Submit",
            style: { display: 'none' },
            id: 'bizyair-upload-submit',
            onclick: () => initUpload.toSubmit() 
        });
        const handleTabItemClass = (ele) => {
            const tabItem = document.querySelectorAll('.bizyair-header-tab-item');
            tabItem.forEach(e => {
                e.className = 'bizyair-header-tab-item'
            })
            ele.className = 'bizyair-header-tab-item bizyair-header-tab-item-active'
        }
        const initUpload = uploadPage(typeListData, submit_button)
        this.initUpload = initUpload
        const content =
            $el("div.comfy-modal-content",
                [
                    $el("div.bizyair-header-tab", {}, [
                        $el('div.bizyair-header-tab-item.bizyair-header-tab-item-active', {
                            onclick: function() {
                                __this.showModel()
                                handleTabItemClass(this)
                                document.querySelector('#bizyair-upload-submit').style.display = 'none'
                            }
                        }, ['My Files']),
                        $el('div.bizyair-header-tab-item', {
                            onclick: function() {
                                __this.showUpload()
                                handleTabItemClass(this)
                                document.querySelector('#bizyair-upload-submit').style.display = 'block'
                            }
                        }, ['Upload'])
                    ]),
                    $el('div.bizyair-d-content-item', {
                        id: 'bizyair-d-model',
                        style: { display: 'block' }
                    }, [ modelList(modelListData, typeListData) ]),
                    $el('div.bizyair-d-content-item', {
                        id: 'bizyair-d-upload',
                        style: { display: 'none' }
                    }, [
                        initUpload.content
                    ]),
                    $el('div.cm-bottom-footer', {}, [submit_button, close_button]),
                ]
            );
        this.element = $el('div.bizyair-modal', {
            parent: document.body,
        }, [
            $el("div.comfy-modal.bizyair-dialog", {
                id: 'bizyair-model-dialog',
                parent: document.body,
                style: { display: 'block' }
            }, [content])
        ])
        document.addEventListener('keydown', (e) => this.keyDown(e));
    }
    showModel() {
        models_files('bizyair/lora').then(res => {
            document.querySelector('#bizyair-d-model').style.display = 'block'
            document.querySelector('#bizyair-d-upload').style.display = 'none'
            document.querySelector('#bizyair-d-model').innerHTML = ''
            document.querySelector('#bizyair-d-model').appendChild(modelList(res.data, this.typeListData))
        })
    }
    showUpload() {
        document.querySelector('#bizyair-d-model').style.display = 'none'
        document.querySelector('#bizyair-d-upload').style.display = 'block'
        this.initUpload.redraw()
    }
    keyDown(e) {
        if (e.key === 'Escape') {
            this.remove();
        }
    }
    remove() {
        this.element.remove()
        document.removeEventListener('keydown', (e) => this.keyDown(e));
    }
    showDialog(listData, typeData) {
        this.element.style.display = "block";
        this.modelListData = listData
        this.typeListData = typeData
    }
}
