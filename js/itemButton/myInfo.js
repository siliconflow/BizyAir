import { $el } from "../../../scripts/ui.js";
import { myInfoDialog } from "../dialog/myInfoPage.js";

export const myInfoBtn = () => {

    return $el('div.menus-item.menus-item-profile', {
        onclick: () => myInfoDialog(),
    }, ['Profile'])
}
