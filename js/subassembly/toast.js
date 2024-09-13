import { $el } from "../../../scripts/ui.js";

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = window.crypto.getRandomValues(new Uint8Array(1))[0] % 16 | (c === 'x' ? 0 : 8);
        return r.toString(16);
    });
}
function removeToast(el) {
    el.style.transition = 'all 0.2s';
    el.style.opacity = '0';
    el.style.transform = 'translate(50%, 0) scale(0)';
    setTimeout(() => {
        el.remove();
    }, 200);
}
export function toast(params) {
    if (typeof params === 'string') {
        params = {
            content: params
        };
    }
    const id = 'bizyair-toast' + generateUUID();
    const style = {
        top: `${document.querySelectorAll('.bizyair-toast').length * 60 + 100}px`
    }
    let iTime = null;
    params.type = params.type || 'succeed';
    $el(`div.bizyair-toast${params.type ? `.bizyair-toast-${params.type}` : ''}`, {
        id,
        style,
        parent: document.body,
    },[
        (params.type && params.type == 'succeed'? $el('div.bizyair-toast-icon.bizyair-toast-icon-succeed', {}, []): ''),
        (params.type && params.type == 'warning'? $el('div.bizyair-toast-icon.bizyair-toast-icon-warning', {}, []): ''),
        (params.type && params.type == 'error'? $el('div.bizyair-toast-icon.bizyair-toast-icon-error', {}, []): ''),
        $el('span.bizyair-toast-content', {}, [params.content]),
        $el('span.bizyair-toast-close', {}, []),
    ]);
    iTime = setTimeout(() => {
        removeToast(document.querySelector(`#${id}`));
        clearTimeout(iTime);
    }, 3000);
    document.querySelector(`#${id} .bizyair-toast-close`).addEventListener('click', () => {
        removeToast(document.querySelector(`#${id}`));
        clearTimeout(iTime);
    });
    document.querySelector(`#${id}`).addEventListener('mouseover', () => {
        clearTimeout(iTime);
    });
    document.querySelector(`#${id}`).addEventListener('mouseout', () => {
        iTime = setTimeout(() => {
            removeToast(document.querySelector(`#${id}`));
            clearTimeout(iTime);
        }, 3000);
    });
}
toast.warning = (params) => {
    toast({
        content: params,
        type: 'warning'
    })
}
toast.error = (params) => {
    toast({
        content: params,
        type: 'error'
    })
}