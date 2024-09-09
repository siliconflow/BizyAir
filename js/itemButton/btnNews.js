import { api } from "../../../scripts/api.js";
import { $el } from "../../../scripts/ui.js";
import { showMenu } from "../subassembly/btnMenuFn.js";

let show_cases = null;
api.fetchApi("/bizyair/news", { method: "GET" }).then(response => response.json()).then(data => {
    show_cases = data
});

export const newsBtn = $el('div.menus-item.menus-item-news', {
    onclick: (e) => showMenu(e, show_cases),
}, ['News', $el('span.menus-item-arrow', {}, [])])