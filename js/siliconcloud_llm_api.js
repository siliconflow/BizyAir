import { app } from "../../scripts/app.js";

const createModelFetchExtension = (nodeName, endpoint) => {
    return {
        name: `bizyair.siliconcloud.${nodeName.toLowerCase()}.api.model_fetch`,
        async beforeRegisterNodeDef(nodeType, nodeData, app) {
            if (nodeData.name === nodeName) {
                const originalNodeCreated = nodeType.prototype.onNodeCreated;
                nodeType.prototype.onNodeCreated = async function () {
                    if (originalNodeCreated) {
                        originalNodeCreated.apply(this, arguments);
                    }

                    const modelWidget = this.widgets.find((w) => w.name === "model");

                    const fetchModels = async () => {
                        try {
                            const response = await fetch(endpoint, {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                },
                                body: JSON.stringify({}),
                            });

                            if (response.ok) {
                                const models = await response.json();
                                console.debug(`Fetched ${nodeName} models:`, models);
                                return models;
                            } else {
                                console.error(`Failed to fetch ${nodeName} models: ${response.status}`);
                                return [];
                            }
                        } catch (error) {
                            console.error(`Error fetching ${nodeName} models`, error);
                            return [];
                        }
                    };

                    const updateModels = async () => {
                        const prevValue = modelWidget.value;
                        modelWidget.value = "";
                        modelWidget.options.values = [];

                        const models = await fetchModels();

                        modelWidget.options.values = models;
                        console.debug(`Updated ${nodeName} modelWidget.options.values:`, modelWidget.options.values);

                        if (models.includes(prevValue)) {
                            modelWidget.value = prevValue; // stay on current.
                        } else if (models.length > 0) {
                            modelWidget.value = models[0]; // set first as default.
                        }

                        console.debug(`Updated ${nodeName} modelWidget.value:`, modelWidget.value);
                        app.graph.setDirtyCanvas(true);
                    };

                    const dummy = async () => {
                        // calling async method will update the widgets with actual value from the browser and not the default from Node definition.
                    };

                    // Initial update
                    await dummy(); // this will cause the widgets to obtain the actual value from web page.
                    await updateModels();
                };
            }
        },
    };
};

// LLM Extension
app.registerExtension(
    createModelFetchExtension(
        "BizyAirSiliconCloudLLMAPI",
        "/bizyair/get_silicon_cloud_llm_models"
    )
);

// VLM Extension
app.registerExtension(
    createModelFetchExtension(
        "BizyAirSiliconCloudVLMAPI",
        "/bizyair/get_silicon_cloud_vlm_models"
    )
);
