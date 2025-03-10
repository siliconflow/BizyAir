import { api } from "../../../scripts/api.js";
import { app } from "../../scripts/app.js";
app.registerExtension({
    name: "bizyair.siliconcloud.share.controlnet.loader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_SharedControlNetLoader") {
            async function onTextChange(share_id, canvas, comfynode) {
                console.log("share_id:", share_id);
                const response = await api.fetchApi(`/bizyair/modelhost/${share_id}/models/files?type=bizyair/controlnet`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                const { data: controlnets } = await response.json();
                const controlnet_name_widget = comfynode.widgets.find(widget => widget.name === "control_net_name");
                if (controlnets.length > 0) {
                    controlnet_name_widget.value = controlnets[0];
                    controlnet_name_widget.options.values = controlnets;
                } else {
                    console.log("No controlnets found in the response");
                    controlnet_name_widget.value = "";
                    controlnet_name_widget.options.values = [];
                }
            }

            function setWigetCallback(){
                const shareid_widget = this.widgets.find(widget => widget.name === "share_id");
                if (shareid_widget) {
                    shareid_widget.callback = onTextChange;
                } else {
                    console.log("share_id widget not found");
                }
            }
            const onNodeCreated = nodeType.prototype.onNodeCreated
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                setWigetCallback.call(this, arguments);
            };
        }
    },
})
