import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "bizyair.siliconcloud.llm.api.populate",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAirSiliconCloudLLMAPI") {
            function populate(text) {
                if (this.widgets) {
                    const pos = this.widgets.findIndex((w) => w.name === "showtext");
                    if (pos !== -1) {
                        for (let i = pos; i < this.widgets.length; i++) {
                            this.widgets[i].onRemove?.();
                        }
                        this.widgets.length = pos;
                    }
                }

                for (const list of text) {
                    const w = ComfyWidgets["STRING"](this, "showtext", ["STRING", { multiline: true }], app).widget;
                    w.inputEl.readOnly = true;
                    w.inputEl.style.opacity = 0.6;
                    w.value = list;
                }

                requestAnimationFrame(() => {
                    const sz = this.computeSize();
                    if (sz[0] < this.size[0]) {
                        sz[0] = this.size[0];
                    }
                    if (sz[1] < this.size[1]) {
                        sz[1] = this.size[1];
                    }
                    this.onResize?.(sz);
                    app.graph.setDirtyCanvas(true, false);
                });
            }

            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);
                populate.call(this, message.text);
            };
        }
    },
});

app.registerExtension({
    name: "bizyair.siliconcloud.llm.api.model_fetch",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAirSiliconCloudLLMAPI") {
            const originalNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = async function () {
                if (originalNodeCreated) {
                    originalNodeCreated.apply(this, arguments);
                }

                const modelWidget = this.widgets.find((w) => w.name === "model");

                const fetchModels = async () => {
                    try {
                        const response = await fetch("/bizyair/get_silicon_cloud_models", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({}),
                        });

                        if (response.ok) {
                            const models = await response.json();
                            console.debug("Fetched models:", models);
                            return models;
                        } else {
                            console.error(`Failed to fetch models: ${response.status}`);
                            return [];
                        }
                    } catch (error) {
                        console.error(`Error fetching models`, error);
                        return [];
                    }
                };

                const updateModels = async () => {
                    const prevValue = modelWidget.value;
                    modelWidget.value = "";
                    modelWidget.options.values = [];

                    const models = await fetchModels();

                    modelWidget.options.values = models;
                    console.debug("Updated modelWidget.options.values:", modelWidget.options.values);

                    if (models.includes(prevValue)) {
                        modelWidget.value = prevValue; // stay on current.
                    } else if (models.length > 0) {
                        modelWidget.value = models[0]; // set first as default.
                    }

                    console.debug("Updated modelWidget.value:", modelWidget.value);
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
});
