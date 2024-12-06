import { app } from "../../scripts/app.js";

import './bizyair_frontend.js'
import { hideWidget } from './subassembly/tools.js'

function createSetWidgetCallback(modelType) {
    return function setWidgetCallback() {
        const lora_name = this.widgets.find(widget => widget.name === "lora_name");
        if (lora_name) {
            lora_name.value = lora_name.value || "to choose"
            lora_name.mouse = function(e, pos, canvas) {
                try {
                    if (e.type === "pointerdown" || e.type === "mousedown" || e.type === "click" || e.type === "pointerup") {
                        e.preventDefault();
                        e.stopPropagation();
                        e.widgetClick = true;
                        
                        const currentNode = this.node;  
                        
                        if (!currentNode || !currentNode.widgets) {
                            console.warn("Node or widgets not available");
                            return false;
                        }
                        
                        if (typeof bizyAirLib !== 'undefined' && typeof bizyAirLib.showModelSelect === 'function') {
                            bizyAirLib.showModelSelect({
                                modelType: [modelType],
                                selectedBaseModels: [],
                                onApply: (version, model) => {
                                    if (!currentNode || !currentNode.widgets) return;
                                    
                                    const currentLora = currentNode.widgets.find(w => w.name === "lora_name");
                                    const currentModel = currentNode.widgets.find(w => w.name === "model_version_id");
                                    
                                    if (model && currentModel && version) {
                                        currentLora.value = model;
                                        currentModel.value = version.id;
                                        currentNode.setDirtyCanvas(true);
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
            
            lora_name.node = this;
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
    
    if (!node._bizyairState) {
        node._bizyairState = {
            lastClickTime: 0,
            DEBOUNCE_DELAY: 300,
            original_onMouseDown: node.onMouseDown
        };
    }
    
    node.onMouseDown = function(e, pos, canvas) {
        if (e.widgetClick) {
            return this._bizyairState.original_onMouseDown?.apply(this, arguments);
        }

        const lora_name = this.widgets.find(widget => widget.name === "lora_name");
        
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
            if (currentTime - this._bizyairState.lastClickTime < this._bizyairState.DEBOUNCE_DELAY) {
                return false;
            }
            this._bizyairState.lastClickTime = currentTime;
            
            const currentNode = this;
            bizyAirLib.showModelSelect({
                modelType: [modelType],
                selectedBaseModels: [],
                onApply: (version, model) => {
                    if (!currentNode || !currentNode.widgets) return;
                    
                    const currentLora = currentNode.widgets.find(w => w.name === "lora_name");
                    const currentModel = currentNode.widgets.find(w => w.name === "model_version_id");
                    
                    if (model && currentModel && version) {
                        currentLora.value = model;
                        currentModel.value = version.id;
                        currentNode.setDirtyCanvas(true);
                    }
                }
            });
            return false;
        } else {
            return this._bizyairState.original_onMouseDown?.apply(this, arguments);
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
