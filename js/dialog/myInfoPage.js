import { drawer } from '../subassembly/drawer.js';
import { $el } from "../../../scripts/ui.js";
import { tooltip } from  '../subassembly/tooltip.js'

export function myInfoDialog(info) {
    console.log(info)
    const editShareId = () => {
        console.log('editShareId')
    }
    const copyShareId = () => {
        console.log('copyShareId')
    }
    const content =
        $el('div', {}, [
            $el('div', {}, [
                // $el('div', {}, [`xxx: ${info.name}`]),
                $el('div.bizyair-myinfo-primary', {}, ['api_key:', $el('span.bizyair-myinfo-password', {}, [`${info.api_key}`])]),
                $el('div.bizyair-myinfo-primary', {}, [`level: ${info.status}`]),
                // $el('div', {}, [`api: ${info.status}`]),
                $el('div.bizyair-myinfo-primary-box', {}, [
                    $el('div.bizyair-myinfo-primary', {}, [ `share_id: ${info.share_id}` ]),
                    $el('div.bizyair-myinfo-operate', {}, [
                        tooltip({
                            tips: 'Edit',
                            content: $el('span.bizyair-icon-operate.bizyair-icon-edit', {
                                onclick: editShareId
                            })
                        }),
                        tooltip({
                            tips: 'Copy',
                            content: $el('span.bizyair-icon-operate.bizyair-icon-copy', {
                                onclick: copyShareId
                            })
                        })
                    ]),
                ]),
            ])
        ])
    drawer({
        title: 'My Info',
        content: content,
        direction: 'right',
        width: '600px'
    });
}
