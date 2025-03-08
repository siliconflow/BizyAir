import { app } from "../../scripts/app.js";


app.registerExtension({
    name: "bizyair.deprecated.nodes",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        const warning_msg = {
            // "BizyAirJoyCaption": "It will be available until 2024/11/16. Please use \"☁️BizyAir Joy Caption2\" node instead.",
        }
        if (Object.keys(warning_msg).includes(nodeData.name)) {
            async function alert_deprecated(node_name, display_name) {
                alert(`${display_name}: ${warning_msg[node_name]}`);
            }
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function (message) {
                onNodeCreated?.apply(this, arguments);
                alert_deprecated.call(this, nodeData.name, nodeData.display_name);
            };
        }
    },
});
