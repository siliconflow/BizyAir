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
            hideWidget(node, "model_version_id");
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
            hideWidget(node, "model_version_id");
        }
    }
})
