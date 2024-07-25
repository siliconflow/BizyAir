import { app } from "../../scripts/app.js";
import { api } from "../../../../scripts/api.js";


app.registerExtension({
    name: "BizyAir_SetAPIKey",

    async setup() {
        const menu = document.querySelector(".comfy-menu");

        // 添加分隔线
        const separator = document.createElement("div");
        separator.style.margin = "20px 0";
        separator.style.width = "100%";
        separator.style.height = "2px";
        separator.style.backgroundColor = "gray";
        menu.append(separator);

        // 创建按钮
        const BizyAir_SetAPIKey = document.createElement("button");
        BizyAir_SetAPIKey.textContent = "BizyAir Key";
        BizyAir_SetAPIKey.style.backgroundColor = "rgb(130, 88, 245)"; // 设置按钮背景颜色
        BizyAir_SetAPIKey.style.border = "none";
        BizyAir_SetAPIKey.style.color = "white";
        BizyAir_SetAPIKey.style.padding = "10px 20px";
        BizyAir_SetAPIKey.style.textAlign = "center";
        BizyAir_SetAPIKey.style.textDecoration = "none";
        BizyAir_SetAPIKey.style.display = "inline-block";
        BizyAir_SetAPIKey.style.fontSize = "16px";
        BizyAir_SetAPIKey.style.margin = "4px 2px";
        BizyAir_SetAPIKey.style.cursor = "pointer";
        BizyAir_SetAPIKey.style.borderRadius = "12px";

        // 动态获取当前页面的协议、地址和端口
        const currentUrl = window.location.protocol + "//" + window.location.host;
        const apiKeyUrl = currentUrl + "/bizyair/set-api-key";

        // 设置按钮点击事件
        BizyAir_SetAPIKey.onclick = () => {
            window.open(apiKeyUrl, "Set API Key");
        };

        menu.append(BizyAir_SetAPIKey);
    }
});



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
        if (nodeData.name === "BizyAirSetAPIKey") {
            async function set_api_key_to_cookies(text) {
                if (text === "sk-****************") {
                    return;
                }
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

                this.widgets[0].value = "sk-****************";
            }
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);
                set_api_key_to_cookies.call(this, message.api_key[0]);
            };
        }
    },
});
