import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "bizyair.siliconcloud.llm.api",
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
                // message is the ui_obj return by python backend {"ui": ui_obj, "result": result_obj}
                onExecuted?.apply(this, arguments);
                // python backend return {"ui": {"text": text}, ...}, so message has the attribute text
                populate.call(this, message.text);
            };
        }
    },
})
