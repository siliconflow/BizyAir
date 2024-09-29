import { api } from "../../../scripts/api.js";
import { app } from "../../scripts/app.js";
app.registerExtension({
    name: "bizyair.siliconcloud.share.lora.loader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_SharedLoraLoader") {
            async function onTextChange(share_id, canvas, comfynode) {
                console.log("share_id:", share_id);
                const response = await api.fetchApi(`/bizyair/modelhost/${share_id}/models/files?type=bizyair/lora`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                const { data: loras_list } = await response.json();
                const lora_name_widget = comfynode.widgets.find(widget => widget.name === "lora_name");
                if (loras_list.length > 0) {
                    lora_name_widget.value = loras_list[0];
                    lora_name_widget.options.values = loras_list;
                } else {
                    console.log("No loras found in the response");
                    lora_name_widget.value = "";
                    lora_name_widget.options.values = [];
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
