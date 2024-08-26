import { $el } from "../../../scripts/ui.js";
import { UploadDialog } from "../dialog/uploadFile.js";
import { ModelDialog } from "../dialog/modelDialog.js";
export const modelBtn = $el('div.menus-item.menus-item-model', {
    onclick: () => showModel(),
}, ['Model'])

const upload = new UploadDialog()
function showModel() {
    upload.showDialog()
}
fetch('/bizyair/modelhost/models/files?type=bizyair/lora', {method: 'GET'}).then(response => response.json()).then(data => {
    console.log(data)
    new ModelDialog().showDialog(data.data)
})
