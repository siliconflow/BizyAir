import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "bizyair.siliconcloud.llm.api",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BizyAirSiliconCloudLLMAPI") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                onNodeCreated?.apply(this, arguments);

                const modelWidget = this.widgets.find(w => w.name === "model");
                if (modelWidget) {
                    modelWidget.options.values = ["Loading..."];
                    fetch('/bizyair/get_silicon_cloud_models', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}),
                    })
                    .then(response => response.json())
                    .then(models => {
                        modelWidget.options.values = models;
                        modelWidget.value = models[0];
                        app.graph.setDirtyCanvas(true);
                    })
                    .catch(error => {
                        console.error('Error fetching models:', error);
                        modelWidget.options.values = ["Error fetching models"];
                        app.graph.setDirtyCanvas(true);
                    });
                }
            };

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
})
