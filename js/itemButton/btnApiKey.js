import { $el } from "../../../scripts/ui.js";
import { apiKey } from "../dialog/apiKey.js";
export const apiKeyBtn = $el('div.menus-item.menus-item-key', {
    onclick: () => showModel(),
}, ['API Key'])

function showModel() {
    apiKey()
}
