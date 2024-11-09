import { app } from "../../scripts/app.js";
import { dialog } from './subassembly/dialog.js'
import { $el } from "../../scripts/ui.js";

import './biz_lib_frontend.js'
app.registerExtension({
    name: "bizyair.siliconcloud.share.lora.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_LoraLoaderNew") {

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
        if (node?.comfyClass === "BizyAir_LoraLoaderNew") {
            const original_onMouseDown = node.onMouseDown;

            let lastClickTime = 0;
            const DEBOUNCE_DELAY = 300; // 300ms防抖延迟

            node.onMouseDown = function( e, pos, canvas ) {
                console.log(this.size)
                const lora_name = this.widgets.find(widget => widget.name === "lora_name")
                if (pos[1] - lora_name.last_y > 0 && pos[1] - lora_name.last_y < 20) {
                    const currentTime = new Date().getTime();
                    if (currentTime - lastClickTime < DEBOUNCE_DELAY) {
                        return false;
                    }
                    lastClickTime = currentTime;

                    const litecontextmenu = document.querySelector('.litegraph.litecontextmenu')
                    if (litecontextmenu) {
                        litecontextmenu.style.display = 'none'
                    }
                    console.log('showModelSelec111t')
                    bizyAirLib.showModelSelect({
                        modelType:"LoRA",
                        selectedBaseModels:["Flux.1 D","SDXL"],
                        onApply: (version,model) => {
                            console.log('version',version)
                            console.log('model',model)
                           // lora_name.value = model.version
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
