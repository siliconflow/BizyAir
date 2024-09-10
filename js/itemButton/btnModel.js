import { $el } from "../../../scripts/ui.js";
// import { UploadDialog } from "../dialog/uploadFile.js";
import { ModelDialog } from "../dialog/modelDialog.js";
import { models_files, model_types } from "../apis.js";
import { showMenu } from "../subassembly/btnMenuFn.js";
import { modelList } from "../dialog/modelList.js";
// import { uploadPage } from "../dialog/uploadFile.js";
import { uploadWithInputPage } from "../dialog/uploadWithInputPage.js";


const show_cases = {
    "Remote Folders": modelList,
    // "Upload": uploadPage,
    "Upload": uploadWithInputPage,
}
export const modelBtn = $el('div.menus-item.menus-item-model', {
    onclick: (e) => showMenu(e, show_cases),
}, ['Model'])


function showModel() {
    Promise.all([
        models_files('bizyair/lora'),
        model_types()
    ]).then(data => {
        new ModelDialog(data[0].data, data[1].data).showDialog(data[0].data, data[1].data);

    }).catch(error => {

    });
}
