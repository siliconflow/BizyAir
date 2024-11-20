import { app } from "../../scripts/app.js";

import './biz_lib_frontend.js'
import { hideWidget } from './subassembly/tools.js'


app.registerExtension({
    name: "bizyair.siliconcloud.share.lora.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_LoraLoader") {

            function setWigetCallback() {
               
            }
            const onNodeCreated = nodeType.prototype.onNodeCreated
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                setWigetCallback.call(this, arguments);
            };
        }
    },



    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_LoraLoader") {
            const original_onMouseDown = node.onMouseDown;

            let lastClickTime = 0;
            const DEBOUNCE_DELAY = 300; // 300ms防抖延迟


            hideWidget(node, "model_version_id");

            node.onMouseDown = function( e, pos, canvas ) {
                const lora_name = this.widgets.find(widget => widget.name === "lora_name")
                const  model_widget = this.widgets.find(widget => widget.name === "model_version_id") // hidden
                if (pos[1] - lora_name.last_y > 0 && pos[1] - lora_name.last_y < 20) {
                    const litecontextmenu = document.querySelector('.litegraph.litecontextmenu')
                    if (litecontextmenu) {
                        litecontextmenu.style.display = 'none'
                    }
                    e.stopImmediatePropagation();
                    e.preventDefault();
                    if (e.button !== 0) {
                        return false;
                    }
                    const currentTime = new Date().getTime();
                    if (currentTime - lastClickTime < DEBOUNCE_DELAY) {
                        return false;
                    }
                    lastClickTime = currentTime;
                    bizyAirLib.showModelSelect({
                        modelType:["LoRA"],
                        selectedBaseModels:["Flux.1 D","SDXL"],
                        onApply: (version,model) => {
                            if(model && model_widget && lora_name && version){
                                lora_name.value = model
                                model_widget.value = version.id
                            }
                        }
                    })
                    return false;
                } else {
                    return original_onMouseDown?.apply(this, arguments);
                }
            }
        }
    }
})




app.registerExtension({
    name: "bizyair.siliconcloud.share.controlnet.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_ControlNetLoader") {

            function setWigetCallback() {
                console.log(this)
            }
            const onNodeCreated = nodeType.prototype.onNodeCreated
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                setWigetCallback.call(this, arguments);
            };
        }
    },



    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_ControlNetLoader") {
            const original_onMouseDown = node.onMouseDown;

            let lastClickTime = 0;
            const DEBOUNCE_DELAY = 300; // 300ms防抖延迟

            hideWidget(node, "model_version_id");

            node.onMouseDown = function( e, pos, canvas ) {
                console.log(this.size, this.widgets)
                const lora_name = this.widgets.find(widget => widget.name === "control_net_name")
                const  model_widget = this.widgets.find(widget => widget.name === "model_version_id") // hidden
                if (pos[1] - lora_name.last_y > 0 && pos[1] - lora_name.last_y < 20) {
                    const litecontextmenu = document.querySelector('.litegraph.litecontextmenu')
                    if (litecontextmenu) {
                        litecontextmenu.style.display = 'none'
                    }
                    e.stopImmediatePropagation();
                    e.preventDefault();
                    if (e.button !== 0) {
                        return false;
                    }
                    const currentTime = new Date().getTime();
                    if (currentTime - lastClickTime < DEBOUNCE_DELAY) {
                        return false;
                    }
                    lastClickTime = currentTime;
                    bizyAirLib.showModelSelect({
                        modelType:["Controlnet"],
                        selectedBaseModels:["Flux.1 D","SDXL"],
                        onApply: (version,model) => {
                            if(model && model_widget && lora_name && version){
                                lora_name.value = model
                                model_widget.value = version.id
                            }
                        }
                    })
                    // const aasd = dialog({
                    //     content: $el('div', {
                    //         style: {
                    //             width: '1000px',
                    //             height: '500px'
                    //         },
                    //         onclick: () => {
                    //             lora_name.value = '123243'
                    //             aasd.close()
                    //         }
                    //     }, ["123"]),
                    //     noText: 'Close',
                    //     onClose: () => {
                    //         console.log('closed')
                    //     }
                    // })
                    return false; // 确保事件结束
                } else {
                    return original_onMouseDown?.apply(this, arguments);
                }
            }
        }
    }
})
