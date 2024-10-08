import { dialog } from '../subassembly/dialog.js';
import { $el } from "../../../scripts/ui.js";
import { delModels, models_files, model_types, change_public } from "../apis.js"
import { subscribe, unsubscribe } from '../subassembly/subscribers.js'

export const modelList = async () => {
    let isPublic = 'false';
    let type = 'bizyair/lora';
    const resType = await model_types();
    const typeList = resType.data;

    const getData = async () => {
        const elItemBody = document.querySelector('#bizyair-model-list-item-body')
        return models_files({type, public: isPublic}).then(res => {
            if (res.code === 20000) {
                elItemBody.innerHTML = ''
                const elData = elDataItem(res.data)
                if (elData.length) {
                    for (const ele of elData) {
                        elItemBody.appendChild(ele)
                    }
                }
            }
        })
    }
    const elDataItemChild = (list) => {
        return list.map(item => $el('div.bizyair-model-list-item-child.bizyair-model-list-item', {}, [
            $el('div.bizyair-flex-item', { title: item.label_path}, [item.label_path]),
            $el('div.bizyair-flex-item', {}, [
                item.available
                    ?
                    $el('span.available-word', {}, ['Available'])
                    :
                    $el('span.spinner-container.spinner-container-in-list', {}, [$el('span.spinner')])
            ]),
            $el('div.bizyair-flex-item-avaulable', {}, [' '])
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
                    type,
                    name,
                }).then(res => {
                    if (res.code === 20000) {
                        ele.closest('.bizyair-model-list-item').remove()
                    }
                })
                return true
            }
        })
    }
    const share = (data, ele) => {
        const changePublic = (publicStatus) => {
            change_public({
                type,
                name: data.name,
                public: publicStatus
            }).then(res => {
                if (res.code === 20000) {
                    ele.closest('.bizyair-model-list-item').remove()
                }
            })
        }
        if (!data.list[0].available) {
            dialog({
                content: "The model is not available, please try again later.",
                noText: 'Close',
                type: 'warning',
            });
            return
        }
        if (data.list[0]?.public) {
            dialog({
                content: "Are you sure you want to cancel this?",
                yesText: "Yes",
                noText: "No",
                onYes: () => {
                    changePublic(false)
                    return true
                }
            })
        } else {
            changePublic(true)
        }
    }

    const handleItemLis = (ele) => {
        ele.className = ele.className === 'bizyair-icon-fold' ? 'bizyair-icon-fold unfold' : 'bizyair-icon-fold';
        ele.closest('.bizyair-model-list-item').querySelector('.bizyair-model-list-item-lis').style.display = ele.closest('.bizyair-model-list-item').querySelector('.bizyair-model-list-item-lis').style.display === 'none' ? 'block' : 'none'
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
                $el('span.bizyair-model-list-content', {}, [
                    $el('span', {}, [e.name]),
                    $el('span.bizyair-model-handle', {}, [
                        (isPublic !== 'true' ?
                            $el('span.bizyair-icon-delete', {
                                onclick: function() {
                                    del(e.name, this)
                                }
                            }) : ''
                        ),
                        $el(`span.bizyair-icon-share${isPublic === 'true' ? '.bizyair-icon-unshared' : ''}`, {
                            onclick: function() {
                                share(e, this)
                            }
                        }),
                    ]),
                ]),
            ]),
            $el('div.bizyair-model-list-item-lis',
                { style: { display: 'none' } },
                elDataItemChild(e.list)
            )
        ]))
    }

    const changeType = (e) => {
        type = e.target.value;
        getData();
    }
    const changePublic = async (e) => {
        isPublic = e.target.value;
        await getData();

    }

    const content = $el('div.bizyair-model-list', {}, [
        $el('div.bizyair-model-filter-item', {}, [
            $el("div.bizyair-model-filter-lis", {}, [
                $el("span.bizyair-filter-label", {}, ['Filter']),
                $el("select.cm-input-item", {
                    id: 'bizyair-model-filter',
                    onchange: (e) => changeType(e)
                }, [
                    ...elOptions
                ]),
            ]),
            $el("div.bizyair-model-filter-lis", {}, [
                $el("span.bizyair-filter-label", {}, ['Public']),
                $el("label.radio-container", {}, [
                    $el("input", {
                        type: 'radio',
                        name: 'isPublic',
                        value: 'false',
                        checked: isPublic === 'false',
                        onchange: (e) => changePublic(e)
                    }),
                    'No'
                ]),
                $el("label.radio-container", {}, [
                    $el("input", {
                        type: 'radio',
                        name: 'isPublic',
                        value: 'true',
                        onchange: (e) => changePublic(e)
                    }),
                    'Yes'
                ]),
            ])
        ]),

        $el('div.bizyair-model-list-item.bizyair-model-list-item-header', {}, [
            $el('div.bizyair-flex-item', {}, ['File Name']),
            $el('div.bizyair-flex-item', {}, ['Status']),
            $el('div.bizyair-flex-item-avaulable', {}, ['Operate']),
        ]),
        $el('div.bizyair-model-list-item-body',
            { id: 'bizyair-model-list-item-body' },
            []
        )
    ]);
    const fnMessage = (data) => {
        const res = JSON.parse(data.data);
        if (res && res.type === "synced") {
            getData();
        }
    }
    subscribe('socketMessage', fnMessage);
    dialog({
        content: content,
        noText: 'Close',
        onNo: () => {
            unsubscribe('socketMessage', fnMessage)
        }
    })
    getData()
}
