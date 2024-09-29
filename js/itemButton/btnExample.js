import { api } from "../../../scripts/api.js";
import { $el } from "../../../scripts/ui.js";
import { showMenu } from "../subassembly/btnMenuFn.js";

let show_cases = null;
api.fetchApi("/bizyair/showcases", { method: "GET" }).then(response => response.json()).then(data => {
    show_cases = data
});


export const exampleBtn = $el('div.menus-item.menus-item-example', {
    onclick: (e) => showMenu(e, show_cases),
}, ['Examples', $el('span.menus-item-arrow', {}, [])])
