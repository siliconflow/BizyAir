import { app } from "../../scripts/app.js";

import './biz_lib_frontend.js'
import { hideWidget } from './subassembly/tools.js'


app.registerExtension({
    name: "bizyair.siliconcloud.share.lora.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_LoraLoaderNew") {
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
        if (node?.comfyClass === "BizyAir_LoraLoaderNew") {
            const original_onMouseDown = node.onMouseDown;

            let lastClickTime = 0;
            const DEBOUNCE_DELAY = 300; 
        
            hideWidget(node, "model_version_id");
                   
            node.onMouseDown = function( e, pos, canvas ) {
                const lora_name = this.widgets.find(widget => widget.name === "lora_name")
               const  model_widget = this.widgets.find(widget => widget.name === "model_version_id")
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
