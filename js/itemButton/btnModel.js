import { $el } from "../../../scripts/ui.js";
// import { UploadDialog } from "../dialog/uploadFile.js";
import { ModelDialog } from "../dialog/modelDialog.js";
export const modelBtn = $el('div.menus-item.menus-item-model', {
    onclick: () => showModel(),
}, ['Model'])

const modelPage = new ModelDialog([], [])
function showModel() {
    Promise.all([
        fetch('/bizyair/modelhost/models/files?type=bizyair/lora', {method: 'GET'}),
        fetch('/bizyair/modelhost/model_types', {method: 'GET'})
    ]).then(responses => {
        return Promise.all(responses.map(response => response.json()));
    }).then(data => {
        modelPage.showDialog(data[0].data, data[1].data);
        // new ModelDialog([], []).showDialog([], []);
    }).catch(error => {
        console.error('请求失败:', error);
    });
}