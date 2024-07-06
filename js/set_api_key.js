import { app } from "../../scripts/app.js";
import { api } from "../../../../scripts/api.js";


app.registerExtension({
    name: "bizyair.set.api.key",
    async setup() {
        const response = await api.fetchApi("/bizyair/get_api_key",
            { method: "GET" });
        if (response.status === 200) {
            console.log("get SiliconCloud api key successfuly")
        } else {
            alert(`Use node 'Set SiliconCloud API Key' first,
you can get your key from cloud.siliconflow.cn,
or you can only use nodes locally.`);
            const text = await response.text();
            console.log("not set api key:", text)
        }

    },
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ComfyAirSetAPIKey") {
            async function set_api_key_to_cookies(text) {
                const body = new FormData();
                body.append("api_key", text);
                const response = await api.fetchApi("/bizyair/set_api_key",
                    {
                        method: "POST",
                        body: body,
                    }
                );

                if (response.status === 200) {
                    console.log("set SiliconCloud api key successfuly")
                } else {
                    alert("Use node 'Set SiliconCloud API Key' first, you can get your key from cloud.siliconflow.cn")
                    const text = await response.text();
                }

                this.widgets[0].value = "****************";
            }
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);
                set_api_key_to_cookies.call(this, message.api_key[0]);
            };
        }
    },
})
