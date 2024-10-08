import { $el } from "../../../scripts/ui.js";


function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = window.crypto.getRandomValues(new Uint8Array(1))[0] % 16 | (c === 'x' ? 0 : 8);
        return r.toString(16);
    });
}
export function tooltip(params) {
    const id = 'bizyair-tooltip' + generateUUID();
    const style = {}
    let iTime = null;
    const showTips = (e) => {
        clearTimeout(iTime);
        const el = document.querySelector(`#${id} .bizyair-tooltip-content`);
        el.style.display = 'block';
        // el.style.left = e.clientX + 'px';
        // el.style.top = e.clientY + 'px';
    }
    const hideTips = (e) => {
        iTime = setTimeout(() => {
            const el = document.querySelector(`#${id} .bizyair-tooltip-content`);
            el.style.display = 'none';
        }, 300)
    }

    return $el("span.bizyair-tooltip", {
        id,
        style: { zIndex: 10000 + document.querySelectorAll('.bizyair-tooltip').length, ...style }
    }, [
        $el('span.bizyair-tooltip-content', {
            style: { display: 'none' },
            onmousemove: showTips,
            onmouseleave: hideTips,
        }, [params.tips]),
        $el('span.bizyair-tooltip-arrow', {

            onmousemove: showTips,
            onmouseleave: hideTips,
        }, [params.content])
    ])

}