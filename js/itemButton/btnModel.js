import { $el } from "../../../scripts/ui.js";
import { ModelDialog } from "../dialog/modelDialog.js";
import { models_files, model_types } from "../apis.js";

export const modelBtn = $el('div.menus-item.menus-item-model', {
    onclick: () => showModel(),
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
