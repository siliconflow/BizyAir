import { dialog } from '../subassembly/dialog.js';
import { $el } from "../../../scripts/ui.js";
import { delModels, models_files, model_types } from "../apis.js"
export const modelList = async () => {
    
    const resList = await models_files('bizyair/lora');
    const resType = await model_types();
    const listData = resList.data;
    const typeList = resType.data;
    const elDataItemChild = (list) => {
        return list.map(item => $el('div.bizyair-model-list-item-child.bizyair-model-list-item', {}, [
            $el('div.bizyair-flex-item', { title: item.label_path}, [item.label_path]),
            $el('div.bizyair-flex-item-avaulable', {}, [
                item.available ? 'Available' : $el('span.spinner-container', {}, [$el('span.spinner')])
            ])
        ]))
    }
    const del = (name, ele) => {
        dialog({
            title: "This operation cannot be undone.",
            content: "Are you sure you want to delete it?",
            yesText: "Yes",
            noText: "No",
            onYes: () => {
                delModels({
                    type: document.querySelector('#bizyair-model-filter').value,
                    name,
                }).then(res => {
                    if (res.code == 20000) {
                        ele.closest('.bizyair-model-list-item').remove()
                    }
                })
                return true
            }
        })
    }
    const handleItemLis = (ele) => {
        ele.className = ele.className == 'bizyair-icon-fold' ? 'bizyair-icon-fold unfold' : 'bizyair-icon-fold';
        ele.closest('.bizyair-model-list-item').querySelector('.bizyair-model-list-item-lis').style.display = ele.closest('.bizyair-model-list-item').querySelector('.bizyair-model-list-item-lis').style.display == 'none' ? 'block' : 'none'
    }

    const elOptions = typeList.map(item => $el("option", { value: item.value }, [item.label]));
    const elDataItem = (list) => {
        return list.map(e => $el('div.bizyair-model-list-item', {}, [
            $el('div.bizyair-model-list-item-folder', {}, [
                $el('span.bizyair-icon-fold', {
                    onclick: function() {
                        handleItemLis(this)
                    }
                }, ['']),
                $el('span', {}, [e.name]),
                $el('span.bizyair-icon-delete', {
                    onclick: function() {
                        del(e.name, this)
                    }
                }),
            ]),
            $el('div.bizyair-model-list-item-lis',
                { style: { display: 'none' } },
                elDataItemChild(e.list)
            )
        ]))
    }

    const changeType = (e) => {
        const elItemBody = document.querySelector('#bizyair-model-list-item-body')
        models_files(e.target.value).then(res => {
            if (res.code == 20000) {
                elItemBody.innerHTML = ''
                const elData = elDataItem(res.data)
                elData.length && elData.forEach(ele => {
                    elItemBody.appendChild(ele)
                });
            }
        })
    }

    const content = $el('div.bizyair-model-list', {}, [
        $el('div.bizyair-model-filter-item', {}, [
            $el("span.bizyair-filter-label", {}, ['Filter']),
            $el("select.cm-input-item", {
                id: 'bizyair-model-filter',
                onchange: (e) => changeType(e)
            }, [
                ...elOptions
            ]),
        ]),

        $el('div.bizyair-model-list-item.bizyair-model-list-item-header', {}, [
            $el('div.bizyair-flex-item', {}, ['File Name']),
            $el('div.bizyair-flex-item-avaulable', {}, ['Status']),
        ]),
        $el('div.bizyair-model-list-item-body',
            { id: 'bizyair-model-list-item-body' },
            elDataItem(listData)
        )
    ]);

    dialog({
        content: content,
        noText: 'Close',
    })
}