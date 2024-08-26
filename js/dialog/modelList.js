import { $el } from "../../../scripts/ui.js";

export const modelList = (listData) => {
    const elDataItem = listData.map(e => $el('div.bizyair-model-list-item', {}, [
        $el('div.bizyair-model-list-item-label', {}, [e.label_path]),
        $el('div.bizyair-model-list-item-available', {}, [`${ e.available ? 'Available' : 'Unavailable' }`])
    ]))
    return $el('div.bizyair-model-list', {}, [
        $el('div.bizyair-model-list-item.bizyair-model-list-item-header', {}, [
            $el('div.bizyair-model-list-item-label', {}, ['File Name']),
            $el('div.bizyair-model-list-item-available', {}, ['Status']),
        ]),
        ...elDataItem
    ])
};