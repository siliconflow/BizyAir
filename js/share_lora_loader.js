import { api } from "../../../scripts/api.js";
import { app } from "../../scripts/app.js";
app.registerExtension({
    name: "bizyair.siliconcloud.share.lora.loader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAir_SharedLoraLoader") {
            async function onTextChange(share_id, canvas, comfynode) {
                if(share_id.length === 25 && share_id.startsWith("clx")){
                    const response = await api.fetchApi("/bizyair/shareloras", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({ share_id: share_id }),
                    });
                    const loras_list = await response.json()
                    const lora_name_widget = comfynode.widgets.find(widget => widget.name === "lora_name");
                    lora_name_widget.value = loras_list[0]
                    lora_name_widget.options.values = loras_list
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
