import { drawer } from '../subassembly/drawer.js';
import { $el } from "../../../scripts/ui.js";
import { tooltip } from  '../subassembly/tooltip.js'
import { getUserInfo, putShareId } from '../apis.js'
import { apiKey } from "./apiKey.js";
import { toast } from '../subassembly/toast.js';

const getSelector = selector => {
    const element = document.querySelector(selector);
    element.css = function (style) {
        Object.assign(this.style, style);
        return this;
    };
    element.text = function (text) {
        this.innerText = text;
        return this;
    };
    element.val = function (val) {
        this.value = val;
        return this;
    };
    return element;
};
export async function myInfoDialog() {
    const res = await getUserInfo()
    const info = res.data
    sessionStorage.setItem('userInfo', JSON.stringify(info))
    const editShareId = () => {
        getSelector('#bizyair-myinfo-share-id').css({ display: 'none' })
        getSelector('#bizyair-myinfo-share-id-edit').css({ display: 'block' })
        getSelector('.bizyair-tooltip-edit').css({ display: 'none' })
        getSelector('.bizyair-tooltip-save').css({ display: 'block' })
    }
    const saveShareId = async () => {
        await putShareId({ share_id: getSelector('#bizyair-myinfo-share-id-edit').value })
        getSelector('#bizyair-myinfo-share-id').css({ display: 'block' })
        getSelector('#bizyair-myinfo-share-id-edit').css({ display: 'none' })
        getSelector('.bizyair-tooltip-save').css({ display: 'none' })
        getSelector('.bizyair-tooltip-edit').css({ display: 'block' })
        getSelector('#bizyair-myinfo-share-id').text(getSelector('#bizyair-myinfo-share-id-edit').value)
    }
    const copyText = text => {
        console.log(text)
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                toast('Text has been copied to the clipboard.');
            }).catch(err => {
                toast.error('Unable to copy text: ', err);
            });
        } else {
            toast.error('The browser does not support the Clipboard API.');
          }
    }
    const content =
        $el('div', {}, [
            $el('div.bizyair-myinfo-primary', {}, [
                $el('div.bizyair-myinfo-primary-box', {}, [
                    'api_key:',
                    $el('span.bizyair-myinfo-password.margin-left-10', {}, [`${info.api_key}`]),
                    $el('div.bizyair-myinfo-operate', {}, [
                        tooltip({
                            tips: 'Edit',
                            content: $el('span.bizyair-icon-operate.bizyair-icon-edit', {
                                onclick: apiKey
                            })
                        }),
                        tooltip({
                            tips: 'Copy',
                            content: $el('span.bizyair-icon-operate.bizyair-icon-copy', {
                                onclick: () => copyText(info.api_key)
                            })
                        })
                    ]),
                ])
            ]),
            $el('div.bizyair-myinfo-primary', {}, [
                'level: ',
                $el('span.margin-left-10', {}, [`${info.status}`]),
            ]),
            $el('div.bizyair-myinfo-primary-box', {}, [
                $el('div.bizyair-myinfo-primary', {
                    style: {
                        display: 'flex',
                        alignItems: 'center'
                    }
                }, [
                    'share_id: ',
                    $el('span.margin-left-10', {
                        style: {
                            display: 'block'
                        },
                        id: 'bizyair-myinfo-share-id'
                    }, [`${info.share_id}`]),
                    $el('input.margin-left-10', {
                        style: {
                            display: 'none'
                        },
                        id: 'bizyair-myinfo-share-id-edit',
                        value: info.share_id,
                        onblur: saveShareId,
                        onkeyup: (e) => {
                            if (e.key === 'Enter') {
                                saveShareId()
                            }
                        }
                    }),
                ]),
                $el('div.bizyair-myinfo-operate', {}, [
                    tooltip({
                        class: 'bizyair-tooltip-edit',
                        style: {
                            display: 'block'
                        },
                        tips: 'Edit',
                        content: $el('span.bizyair-icon-operate.bizyair-icon-edit', {
                            onclick: editShareId
                        })
                    }),
                    tooltip({
                        class: 'bizyair-tooltip-save',
                        style: {
                            display: 'none'
                        },
                        tips: 'Edit',
                        content: $el('span.bizyair-icon-operate.bizyair-icon-save', {
                            onclick: saveShareId
                        })
                    }),
                    tooltip({
                        tips: 'Copy',
                        content: $el('span.bizyair-icon-operate.bizyair-icon-copy', {
                            onclick: () => copyText(info.share_id)
                        })
                    })
                ]),
            ]),
        ])
    drawer({
        title: 'My Info',
        content: content,
        direction: 'right',
        width: '600px'
    });
}
