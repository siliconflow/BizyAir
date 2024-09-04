import { $el } from "../../../scripts/ui.js";
// import { UploadDialog } from "../dialog/uploadFile.js";
import { ModelDialog } from "../dialog/modelDialog.js";
import { models_files, model_types } from "../apis.js";

export const modelBtn = $el('div.menus-item.menus-item-model', {
    onclick: () => showModel(),
}, ['Model'])

// const upload = new UploadDialog()
function showModel() {
    Promise.all([
        models_files('bizyair/lora'),
        model_types()
    ]).then(data => {
        new ModelDialog(data[0].data, data[1].data).showDialog(data[0].data, data[1].data);
        // new ModelDialog([], []).showDialog([], []);
    }).catch(error => {
        // console.error('请求失败:', error);
    });
}
