import { drawer } from '../subassembly/drawer.js';
import { $el } from "../../../scripts/ui.js";
import { tooltip } from  '../subassembly/tooltip.js'
import { getUserInfo, putShareId } from '../apis.js'
import { apiKey } from "./apiKey.js";
import { toast } from '../subassembly/toast.js';
import { subscribe } from "../subassembly/subscribers.js";

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
const levelMap = {
    1: 'Trial',
    2: 'Pro',
    3: 'Enterprise'
}
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
        toast('Save successfully')
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
                $el('div', {}, [
                    $el('img', { src: 'data:image/png;base64,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' }),
                ]),
                (info.name ? $el('div', {}, [`${info.name}`]) : '')
            ]),

            $el('div.bizyair-myinfo-primary', {}, [
                $el('div.bizyair-myinfo-primary-box', {}, [
                    'Api Key:',
                    $el('span.bizyair-myinfo-password.margin-left-10', {
                        id: 'bizyair-myinfo-password'
                    }, [`${info.api_key}`]),
                    $el('div.bizyair-myinfo-operate', {}, [
                        tooltip({
                            tips: 'Edit',
                            content: $el('span.bizyair-icon-operate.bizyair-icon-edit', {
                                onclick: apiKey
                            })
                        })
                    ]),
                ])
            ]),
            $el('div.bizyair-myinfo-primary', {}, [
                'Status: ',
                $el('span.margin-left-10', {}, [`${info.status}`]),
            ]),
            $el('div.bizyair-myinfo-primary', {}, [
                'Level: ',
                $el('span.margin-left-10', {}, [`${levelMap[info.level]}`]),
            ]),
            $el('div.bizyair-myinfo-primary-box', {}, [
                $el('div.bizyair-myinfo-primary', {
                    style: {
                        display: 'flex',
                        alignItems: 'center'
                    }
                }, [
                    'Share ID: ',
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
                    (Date.now() - new Date(info.last_share_id_update_at) > 1000 * 60 * 60 * 24 * 365 ? tooltip({
                        class: 'bizyair-tooltip-edit',
                        style: {
                            display: 'block'
                        },
                        tips: 'Edit',
                        content: $el('span.bizyair-icon-operate.bizyair-icon-edit', {
                            onclick: editShareId
                        })
                    }): ''),
                    tooltip({
                        class: 'bizyair-tooltip-save',
                        style: {
                            display: 'none'
                        },
                        tips: 'Save',
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
        title: ' ',
        content: content,
        direction: 'right',
        width: '600px'
    });
    subscribe('loginRefresh', e => {
        getSelector('#bizyair-myinfo-password').text(e)
    })
}
