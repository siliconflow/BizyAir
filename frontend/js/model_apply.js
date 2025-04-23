import { app } from "../../scripts/app.js";

import './bizyair_frontend.js'
import { hideWidget } from './subassembly/tools.js'

const possibleWidgetNames=[
    "clip_name",
    "clip_name1",
    "clip_name2",
    "ckpt_name",
    "lora_name",
    "control_net_name",
    "ipadapter_file",
    "unet_name",
    "vae_name",
    "model_name",
    "instantid_file",
    "pulid_file",
    "style_model_name",
]
function createSetWidgetCallback(modelType, selectedBaseModels = []) {
    return function setWidgetCallback() {
        const targetWidget = this.widgets.find(widget => possibleWidgetNames.includes(widget.name));
        if (targetWidget) {
            targetWidget.value = targetWidget.value || "to choose"
            targetWidget.mouse = function(e, pos, canvas) {
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
                                selectedBaseModels,
                                onApply: (version, model) => {
                                    if (!currentNode || !currentNode.widgets) return;

                                    const currentLora = currentNode.widgets.find(widget => possibleWidgetNames.includes(widget.name));
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

            targetWidget.node = this;
            targetWidget.options = targetWidget.options || {};
            targetWidget.options.values = () => [];
            targetWidget.options.editable = false;
            targetWidget.clickable = true;
            targetWidget.processMouse = true;
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



        const targetWidget = this.widgets.find(widget => possibleWidgetNames.includes(widget.name));
        if (targetWidget && pos[1] - targetWidget.last_y > 0 && pos[1] - targetWidget.last_y < 20) {
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

                    const currentLora = currentNode.widgets.find(widget => possibleWidgetNames.includes(widget.name));
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

const nodeDataNames = {
    LoRA: ["BizyAir_LoraLoader","BizyAir_NunchakuFluxLoraLoader"],
    Controlnet: "BizyAir_ControlNetLoader",
    Checkpoint: "BizyAir_CheckpointLoaderSimple",
    // Clip: "BizyAir_CLIPVisionLoader",
    // Ipadapter: "BizyAir_IPAdapterModelLoade",
    // Unet: "BizyAir_MZ_KolorsUNETLoaderV2",
    // Vae: "BizyAir_VAELoader",
    // Upscale_models: "BizyAir_UpscaleModelLoader",
    // Instantid: "BizyAir_InstantIDModelLoader",
    // Pulid: "BizyAir_PulidFluxModelLoader"
}
app.registerExtension({
    name: "bizyair.siliconcloud.share.lora.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        for( const key in nodeDataNames){
            const names = nodeDataNames[key];
            const isMatch = Array.isArray(names) ?
                names.includes(nodeData.name) :
                (nodeData.name === names);

            if(isMatch){
                const onNodeCreated = nodeType.prototype.onNodeCreated;
                nodeType.prototype.onNodeCreated = function() {
                    try {
                        const result = onNodeCreated?.apply(this, arguments);
                        let selectedBaseModels = [];if (nodeData.name === nodeDataNames.Checkpoint) {
                            selectedBaseModels = ['SDXL', 'Pony', 'SD 3.5', 'Illustrious']
                        }
                        createSetWidgetCallback(key, selectedBaseModels).call(this);
                        return result;
                    } catch (error) {
                        console.error("Error in node creation:", error);
                    }
                };
            }
        }
    },

    async nodeCreated(node) {
        for (const key in nodeDataNames) {

            const names = nodeDataNames[key]; //  string | array | undefined
            const isMatch = names ?
                (Array.isArray(names) ? names.includes(node?.comfyClass) : node?.comfyClass === names)
                : false;

            if (isMatch) {
                setupNodeMouseBehavior(node, key);
            }
        }
    }
})
