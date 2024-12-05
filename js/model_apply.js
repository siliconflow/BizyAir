import { app } from "../../scripts/app.js";

import './bizyair_frontend.js'
import { hideWidget } from './subassembly/tools.js'

function createSetWidgetCallback(modelType) {
    return function setWidgetCallback() {
        const lora_name = this.widgets.find(widget => widget.name === "lora_name");
        const model_widget = this.widgets.find(widget => widget.name === "model_version_id");
        if (lora_name) {
            const node = this;
            lora_name.value = lora_name.value || "to choose"
            lora_name.mouse = function(e, pos, canvas) {
                try {
                    if (e.type === "pointerdown" || e.type === "mousedown" || e.type === "click" || e.type === "pointerup") {
                        e.preventDefault();
                        e.stopPropagation();

                        if (typeof bizyAirLib !== 'undefined' && typeof bizyAirLib.showModelSelect === 'function') {
                            bizyAirLib.showModelSelect({
                                modelType: [modelType],
                                selectedBaseModels: [],
                                onApply: (version, model) => {
                                    if (model && model_widget && version) {
                                        lora_name.value = model;
                                        model_widget.value = version.id;
                                        node.setDirtyCanvas(true);
                                    }
                                }
                            });
                        } else {
                            console.error("bizyAirLib not available");
                        }
                        return false;
                    }
                } catch (error) {
                    console.error("Error handling mouse event:", error);
                }
            };
            lora_name.options = lora_name.options || {};
            lora_name.options.values = () => [];
            lora_name.options.editable = false;
            lora_name.clickable = true;
            lora_name.processMouse = true;
        }
    }
}

function setupNodeMouseBehavior(node, modelType) {
    hideWidget(node, "model_version_id");
    let lastClickTime = 0;
    const DEBOUNCE_DELAY = 300;
    node.onMouseDown = function(e, pos, canvas) {
        const lora_name = this.widgets.find(widget => widget.name === "lora_name")
        const model_widget = this.widgets.find(widget => widget.name === "model_version_id") // hidden
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
                modelType: [modelType],
                selectedBaseModels: [],
                onApply: (version, model) => {
                    if (model && model_widget && lora_name && version) {
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

app.registerExtension({
    name: "bizyair.siliconcloud.share.lora.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_LoraLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("LoRA").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_LoraLoader") {
            setupNodeMouseBehavior(node, "LoRA");
        }
    }
})

app.registerExtension({
    name: "bizyair.siliconcloud.share.controlnet.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_ControlNetLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("LoRA").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_ControlNetLoader") {
            setupNodeMouseBehavior(node, "LoRA");
        }
    }
})
