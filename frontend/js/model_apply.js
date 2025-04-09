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
function createSetWidgetCallback(modelType) {
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
                    createSetWidgetCallback("Controlnet").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_ControlNetLoader") {
            setupNodeMouseBehavior(node, "Controlnet");
        }
    }
})



app.registerExtension({
    name: "bizyair.siliconcloud.share.checkpoint.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_CheckpointLoaderSimple") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Checkpoint").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_CheckpointLoaderSimple") {
            setupNodeMouseBehavior(node, "Checkpoint");
        }
    }
})


app.registerExtension({
    name: "bizyair.siliconcloud.share.clipvision.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_CLIPVisionLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Clip").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_CLIPVisionLoader") {
            setupNodeMouseBehavior(node, "Clip");
        }
    }
})

app.registerExtension({
    name: "bizyair.siliconcloud.share.clip.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // console.log(nodeData.name)
        if (nodeData.name === "BizyAir_DualCLIPLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Clip").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_DualCLIPLoader") {
            setupNodeMouseBehavior(node, "Clip");
        }
    }
})

app.registerExtension({
    name: "bizyair.siliconcloud.share.ipadapter.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // console.log(nodeData.name)
        if (nodeData.name === "BizyAir_IPAdapterModelLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Ipadapter").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_IPAdapterModelLoader") {
            setupNodeMouseBehavior(node, "Ipadapter");
        }
    }
})

app.registerExtension({
    name: "bizyair.siliconcloud.share.unet.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log(nodeData.name)
        if (nodeData.name === "BizyAir_MZ_KolorsUNETLoaderV2" || nodeData.name === "BizyAir_UNETLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Unet").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_MZ_KolorsUNETLoaderV2" || node?.comfyClass === "BizyAir_UNETLoader") {
            setupNodeMouseBehavior(node, "Unet");
        }
    }
})

app.registerExtension({
    name: "bizyair.siliconcloud.share.vae.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log(nodeData.name)
        if (nodeData.name === "BizyAir_VAELoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Vae").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_VAELoader") {
            setupNodeMouseBehavior(node, "Vae");
        }
    }
})

app.registerExtension({
    name: "bizyair.siliconcloud.share.upscale.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log(nodeData.name)
        if (nodeData.name === "BizyAir_UpscaleModelLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Upscale_models").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_UpscaleModelLoader") {
            setupNodeMouseBehavior(node, "Upscale_models");
        }
    }
})

app.registerExtension({
    name: "bizyair.siliconcloud.share.instantid.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log(nodeData.name)
        if (nodeData.name === "BizyAir_InstantIDModelLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Instantid").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_InstantIDModelLoader") {
            setupNodeMouseBehavior(node, "Instantid");
        }
    }
})

app.registerExtension({
    name: "bizyair.siliconcloud.share.pulid.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log(nodeData.name)
        if (nodeData.name === "BizyAir_PulidFluxModelLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Pulid").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_PulidFluxModelLoader") {
            setupNodeMouseBehavior(node, "Pulid");
        }
    }
})

app.registerExtension({
    name: "bizyair.siliconcloud.share.style.loader.new",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log(nodeData.name)
        if (nodeData.name === "BizyAir_StyleModelLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback("Style_models").call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_StyleModelLoader") {
            setupNodeMouseBehavior(node, "Style_models");
        }
    }
})
