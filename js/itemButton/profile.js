import { $el } from "../../../scripts/ui.js";
import { profileDialog } from "../dialog/profilePage.js";

export const profileBtn = () => {

    return $el('div.menus-item.menus-item-profile', {
        onclick: () => profileDialog(),
    }, ['Profile'])
}
