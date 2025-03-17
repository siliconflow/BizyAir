import { app, ComfyApp } from "../../scripts/app.js";
import { api } from "../../../scripts/api.js";

app.registerExtension({
	name: "bizyair.tool",
	setup() {

        async function handleFile(json_data) {
            const jsonContent = json_data

            await app.loadGraphData(
                jsonContent,
                true,
                false,
                "convert_test"
              );

        }
        async function convert(){
            const p2 = await app.graphToPrompt();
            const json = JSON.stringify(p2["workflow"], null, 2);

            await api.fetchApi("/bizyair/node_converter", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: json
              }).then(response => response.json())
              .then(data => handleFile(data))
              .catch(error => console.error("Error:", error));
        }
        // Add canvas menu options
        const orig = LGraphCanvas.prototype.getCanvasMenuOptions;
        LGraphCanvas.prototype.getCanvasMenuOptions = function () {
            const options = orig.apply(this, arguments);
            options.push(null, {
                content: "BizyAir Tools",
                submenu: {
                    options: [
                        {
                            content: "convert to bizyair node",
                            callback: async () => {
                                await convert()
                            },
                        },
                    ],
                },
            });
            return options;
        };

	},
});
