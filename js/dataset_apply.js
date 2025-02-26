import { app } from "../../scripts/app.js";

import './bizyair_frontend.js'
import { hideWidget } from './subassembly/tools.js'

function createSetWidgetCallback() {
    return function setWidgetCallback() {
        const targetWidget = this.widgets.find(widget => widget.name == "dataset_path");
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

                        if (typeof bizyAirLib !== 'undefined' && typeof bizyAirLib.showDatasetSelect === 'function') {
                            bizyAirLib.showDatasetSelect({
                                showDatasetSelect: true,
                                isNodeSelect: true,
                                onApply: (versionId, name) => {
                                    console.log("onApply", versionId, name)
                                    if (!currentNode || !currentNode.widgets) return;

                                    const datasetPath = currentNode.widgets.find(widget => widget.name == "dataset_path");
                                    const datasetVersionId = currentNode.widgets.find(w => w.name === "dataset_version_id");
                                    if (datasetPath && datasetVersionId) {
                                        datasetPath.value = name;
                                        datasetVersionId.value = versionId;
                                        currentNode.setDirtyCanvas(true);
                                    }
                                }
                            })
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

function setupNodeMouseBehavior(node) {
    hideWidget(node, "dataset_version_id");

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
        const targetWidget = this.widgets.find(widget => widget.name == "dataset_path");
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
            bizyAirLib.showDatasetSelect({
                showDatasetSelect: true,
                isNodeSelect: true,
                onApply: (versionId, name) => {
                    console.log("onApply", versionId, name)
                    if (!currentNode || !currentNode.widgets) return;

                    const datasetPath = currentNode.widgets.find(widget => widget.name == "dataset_path");
                    const datasetVersionId = currentNode.widgets.find(w => w.name === "dataset_version_id");
                    if (datasetPath && datasetVersionId) {
                        datasetPath.value = name;
                        datasetVersionId.value = versionId;
                        currentNode.setDirtyCanvas(true);
                    }
                }
            })
            return false;
        } else {
            return this._bizyairState.original_onMouseDown?.apply(this, arguments);
        }
    }
}

app.registerExtension({
    name: "bizyair.siliconcloud.share.dataset.loader.train",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_TrainDatasetAdd") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const result = onNodeCreated?.apply(this, arguments);
                    createSetWidgetCallback().call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "BizyAir_TrainDatasetAdd") {
            setupNodeMouseBehavior(node);
        }
    }
})
