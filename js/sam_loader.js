import { app, ComfyApp } from "../../scripts/app.js";
import { sam_edit } from "./dialog/sam_edit.js";
import { api } from "../../../scripts/api.js";

app.registerExtension({
    name: "bizyair.sam.nodes",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {

        if(nodeData.name === "BizyAirSegmentAnythingBox" || nodeData.name === "BizyAirSegmentAnythingPoint"){
            console.log("beforeRegisterNodeDef")
            const original_getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;

            nodeType.prototype.getExtraMenuOptions = function(_, options) {
                original_getExtraMenuOptions?.apply(this, arguments);
                options.push({
                    content: "sam_edit",
                    callback: async () => {
                        ComfyApp.copyToClipspace(this);
                        ComfyApp.clipspace_return_node = this;
                        sam_edit()

                    }
                })
            }
    }


    },
    async nodeCreated(node){

        function showImage(name) {
            const img = new Image();
            img.onload = () => {
                node.imgs = [img];
                app.graph.setDirtyCanvas(true);
            };
            let folder_separator = name.lastIndexOf("/");
            let subfolder = "";
            if (folder_separator > -1) {
                subfolder = name.substring(0, folder_separator);
                name = name.substring(folder_separator + 1);
            }
            img.src = api.apiURL(
                `/view?filename=${encodeURIComponent(name)}&type=input&subfolder=${subfolder}${app.getPreviewFormatParam()}${app.getRandParam()}`
            );
            node.setSizeForImage?.();
        }
        async function reset_sam(){
            await api.fetchApi("/bizyair/resetsam");
        }

        if(node.title === "☁️BizyAir Point Guided SAM" || node.title === "☁️BizyAir Box Guided SAM"){
            console.log("nodeCreated")
            const imageWidget = node.widgets.find(widget => widget.name === "image");
            const cb = node.callback;
            if (imageWidget) {
                imageWidget.callback = async function(){
                    console.log("why my imageWidget callback")
                    showImage(imageWidget.value);
                    if (cb) {
                        return cb.apply(this, arguments);
                    }
                    await reset_sam();
                };
            } else {
                console.log("image widget not found");
            }

        }
    }

});
