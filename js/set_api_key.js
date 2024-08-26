// import { app } from "../../scripts/app.js";
// import { api } from "../../scripts/api.js";

// app.registerExtension({
//     name: "BizyAir_SetAPIKey",

//     async setup() {
//         const menu = document.querySelector(".comfy-menu");
//         // app.ui.dialog.show(`Installing... 'asd'`);
//         // 添加分隔线
//         const separator = document.createElement("div");
//         separator.style.margin = "20px 0";
//         separator.style.width = "100%";
//         separator.style.height = "2px";
//         separator.style.backgroundColor = "gray";
//         menu.append(separator);

//         // 创建按钮
//         const BizyAir_SetAPIKey = document.createElement("button");
//         BizyAir_SetAPIKey.textContent = "BizyAir Key";
//         BizyAir_SetAPIKey.style.backgroundColor = "rgb(130, 88, 245)"; // 设置按钮背景颜色
//         BizyAir_SetAPIKey.style.border = "none";
//         BizyAir_SetAPIKey.style.color = "white";
//         BizyAir_SetAPIKey.style.padding = "10px 20px";
//         BizyAir_SetAPIKey.style.textAlign = "center";
//         BizyAir_SetAPIKey.style.textDecoration = "none";
//         BizyAir_SetAPIKey.style.display = "inline-block";
//         BizyAir_SetAPIKey.style.fontSize = "16px";
//         BizyAir_SetAPIKey.style.margin = "4px 2px";
//         BizyAir_SetAPIKey.style.cursor = "pointer";
//         BizyAir_SetAPIKey.style.borderRadius = "12px";

//         const apiKeyUrl = `${location.href.replace(/\/$/, '')}/bizyair/set-api-key`;
//         BizyAir_SetAPIKey.onclick = () => {
//             window.open(apiKeyUrl, "Set API Key");
//         };

//         menu.append(BizyAir_SetAPIKey);

//         const response = await api.fetchApi("/bizyair/get_api_key",
//             { method: "GET" });
//         if (response.status === 200) {
//             console.log("get SiliconCloud api key successfuly")
//         } else {
//             alert(`Please click "BizyAir Key" button to set API key first,
// you can get your key from cloud.siliconflow.cn,
// or you can only use nodes locally.`);
//             const text = await response.text();
//             console.log("not set api key:", text)
//         }
//     }
// });
