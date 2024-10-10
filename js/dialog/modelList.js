import { dialog } from '../subassembly/dialog.js';
import { $el } from "../../../scripts/ui.js";
import { delModels, models_files, model_types, change_public, getDescription, putDescription } from "../apis.js"
import { subscribe, unsubscribe } from '../subassembly/subscribers.js'
import { tooltip } from  '../subassembly/tooltip.js'

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
    const saveDescription = async (e) => {
        const description = document.querySelector('textarea.bizyair-model-details-item-value').value
        const res = await putDescription({
            type,
            name: e.name,
            description
        })
        if (res) {
            document.querySelector('#description-textarea').style.display = 'none'
            document.querySelector('#description-save').style.display = 'none'
            document.querySelector('#description-word').style.display = 'block'
            document.querySelector('#description-edit').style.display = 'block'
            document.querySelector('#description-word').innerHTML = description
        }
    }
    const detailsItem = (label, value) => {
        return $el('div.bizyair-model-details-item', {}, [
            $el('div.bizyair-model-details-item-label', {}, [label]),
            $el('div.bizyair-model-details-item-value', {}, [value])
        ])
    }
    const showDetails = async (e, ele) => {
        console.log(e, ele)
        let descriptionParam = {
            name: e.name,
            type
        }
        if (isPublic === 'true') {
            descriptionParam = {
                name: e.name,
                type,
                share_id: JSON.parse(sessionStorage.getItem('userInfo')).share_id
            }
        }
        const res = await getDescription(descriptionParam)
        console.log(res)
        // putDescription
        dialog({
            title: "Details",
            content: $el('div.bizyair-model-details', {}, [
                detailsItem('Name', e.name),
                detailsItem('isPublic', isPublic === 'true' ? 'Yes' : 'No'),
                detailsItem('Number of files', e.list.length),
                (
                    isPublic === 'true' ?
                    detailsItem('Share ID', JSON.parse(sessionStorage.getItem('userInfo')).share_id)
                    : ''
                ),
                detailsItem('Description', $el('div.bizyair-model-details-item-value-description', {}, [
                    $el('div.bizyair-model-details-item-value', {
                        style: {
                            display: 'block'
                        },
                        id: 'description-word'
                    }, [res.data.description ? res.data.description : 'No description']),
                    $el('textarea.bizyair-model-details-item-value', {
                        style: {
                            display: 'none'
                        },
                        rows: 6,
                        id: 'description-textarea'
                    }, [res.data.description ? res.data.description : '']),
                    $el('span.bizyair-icon-operate.bizyair-icon-edit', {
                        id: 'description-edit',
                        onclick: () => {
                            document.querySelector('#description-textarea').style.display = 'block'
                            document.querySelector('#description-word').style.display = 'none'
                            document.querySelector('#description-edit').style.display = 'none'
                            document.querySelector('#description-save').style.display = 'block'
                            document.querySelector('#description-textarea').focus()
                        }
                    }, [])
                ])),
                detailsItem(' ', $el('button.bizyair-model-details-item-button', {
                    style: {
                        display: 'none'
                    },
                    id: 'description-save',
                    onclick: () => saveDescription(e)
                }, ['Save'])),


                // $el('div.bizyair-model-details-item', {}, [
                //     $el('div.bizyair-model-details-item-label', {}, ['Name']),
                //     $el('div.bizyair-model-details-item-value', {}, [e.name])
                // ]),
                // $el('div.bizyair-model-details-item', {}, [
                //     $el('div.bizyair-model-details-item-label', {}, ['isPublic']),
                //     $el('div.bizyair-model-details-item-value', {}, [isPublic === 'true' ? 'Yes' : 'No'])
                // ]),
                // $el('div.bizyair-model-details-item', {}, [
                //     $el('div.bizyair-model-details-item-label', {}, ['Number of files']),
                //     $el('div.bizyair-model-details-item-value', {}, [e.list.length])
                // ]),
                // $el('div.bizyair-model-details-item', {
                //     style: {
                //         display: isPublic === 'true' ? 'block' : 'none'
                //     }
                // }, [
                //     $el('div.bizyair-model-details-item-label', {}, ['Share ID']),
                //     $el('div.bizyair-model-details-item-value', {}, [JSON.parse(sessionStorage.getItem('userInfo')).share_id])
                // ]),

                // $el('div.bizyair-model-details-item', {}, [
                //     $el('div.bizyair-model-details-item-label', {}, ['Description']),
                //     $el('div.bizyair-model-details-item-value', {
                //         style: {
                //             display: 'none'
                //         }
                //     }, [`${res.data.description ? res.data.description : 'No description'}`]),
                //     $el('textarea.bizyair-model-details-item-value', {
                //         style: {
                //             display: 'block'
                //         }
                //     }, [`${res.data.description ? res.data.description : 'No description'}`]),

                // ]),
                // $el('div.bizyair-model-details-item', {}, [
                //     $el('button.bizyair-model-details-item-button', {
                //         onclick: () => saveDescription(e)
                //     }, ['Save'])
                // ])
            ]),
            noText: "Close",
        })
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
                        tooltip({
                            tips: 'Details',
                            content: $el('span.bizyair-icon-operate.bizyair-icon-more', {
                                onclick: function() {
                                    showDetails(e, this)
                                }
                            })
                        }),
                        (isPublic !== 'true' ?
                            tooltip({
                                tips: 'Delete',
                                content: $el('span.bizyair-icon-operate.bizyair-icon-delete', {
                                    onclick: function() {
                                        del(e.name, this)
                                    }
                                })
                            })
                            : ''
                        ),
                        tooltip({
                            tips: isPublic === 'true' ? 'Cancel sharing' : 'Share',
                            content: $el(`span.bizyair-icon-operate.bizyair-icon-share${isPublic === 'true' ? '.bizyair-icon-unshared' : ''}`, {
                                onclick: function() {
                                    share(e, this)
                                }
                            })
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
