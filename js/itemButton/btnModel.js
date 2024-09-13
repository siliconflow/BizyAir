import { $el } from "../../../scripts/ui.js";
import { showMenu } from "../subassembly/btnMenuFn.js";
import { modelList } from "../dialog/modelList.js";
import { uploadWithInputPage } from "../dialog/uploadWithInputPage.js";


const show_cases = {
    "Remote Folders": modelList,
    "Upload": uploadWithInputPage,
}
export const modelBtn = $el('div.menus-item.menus-item-model', {
    onclick: (e) => showMenu(e, show_cases),
}, ['Model'])