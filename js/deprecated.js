import { app } from "../../scripts/app.js";


app.registerExtension({
    name: "bizyair.deprecated.nodes",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        const warning_msg = {
            //"BizyAirImageCaption": "It will be available until 2024/08/18. Please use \"☁️BizyAir Joy Caption\" node instead.",
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
