import { $el } from "../../../scripts/ui.js";
import { ConfirmDialog } from "../subassembly/confirm.js";
export const modelList = (listData, typeList) => {
    const elDataItemChild = (list) => {
        return list.map(item => $el('div.bizyair-model-list-item-child.bizyair-model-list-item', {}, [
            $el('div.bizyair-flex-item', {}, ['']),
            $el('div.bizyair-flex-item', {}, [item.label_path]),
            $el('div.bizyair-flex-item-avaulable', {}, [`${ item.available ? 'Available' : 'Unavailable' }`])
        ]))
    }
    const del = (name, ele) => {
        new ConfirmDialog({
            title: "This action cannot be undone.",
            message: "Are you sure you want to delete it?",
            yesText: "Yes",
            noText: "No",
            onYes: () => {
                fetch(`/bizyair/modelhost/models`, {
                    method: 'DELETE',
                    body: JSON.stringify({
                        type: document.querySelector('#bizyair-model-filter').value,
                        name,
                    }),
                }).then(res => res.json()).then(res => {
                    if (res.code == 20000) {
                        ele.closest('.bizyair-model-list-item').remove()
                    }
                })
            }
        })
    }
    const handleItemLis = (ele) => {
        ele.textContent = ele.textContent == '－' ? '＋' : '－';
        ele.closest('.bizyair-model-list-item').querySelector('.bizyair-model-list-item-lis').style.display = ele.closest('.bizyair-model-list-item').querySelector('.bizyair-model-list-item-lis').style.display == 'none' ? 'block' : 'none'
    }

    const elOptions = typeList.map(item => $el("option", { value: item.value }, [item.label]));
    const elDataItem = (list) => {
        return list.map(e => $el('div.bizyair-model-list-item', {}, [
            $el('div.bizyair-model-list-item-folder', {}, [
                $el('span.bizyair-icon-unfold', {
                    onclick: function() {
                        handleItemLis(this)
                    }
                }, ['－']),
                $el('span', {}, [e.name]),
                $el('span.bizyair-icon-delete', {
                    onclick: function() {
                        del(e.name, this)
                    }
                }),
            ]),
            $el('div.bizyair-model-list-item-lis',
                {},
                elDataItemChild(e.list)
            ),
        ]))
    }

    const changeType = (e) => {
        const elItemBody = document.querySelector('#bizyair-model-list-item-body')
        fetch(`/bizyair/modelhost/models/files?type=${e.target.value}`, {method: 'GET'}).then(res => res.json()).then(res => {
            elItemBody.innerHTML = ''
            elDataItem(res.data).foreach(ele => {
                elItemBody.appendChild(ele)
            })
        })
    }


    return $el('div.bizyair-model-list', {}, [
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
            $el('div.bizyair-flex-item', {}, ['Folder']),
            $el('div.bizyair-flex-item', {}, ['File Name']),
            $el('div.bizyair-flex-item-avaulable', {}, ['Status']),
        ]),
        $el('div',
            { id: 'bizyair-model-list-item-body' },
            elDataItem(listData)
        )
    ])
};
