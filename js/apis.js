import { ConfirmDialog } from './subassembly/confirm.js';

function customFetch(url, options = {}) {
    return window.fetch(url, options)
        .then(response => {
            // if (!response.ok) {
            //     const status = response.status ? response.status : ''
            //     const statusText = response.statusText ? response.statusText : ''
            //     app.ui.dialog.show(`HTTP error! \n Status: ${status} \n message: ${statusText}`)
            //     throw new Error(`HTTP error! Status: ${response.status}`);
            // }
            console.log(response)
            return response.json();
        })
        .then(data => {
            const { code, message } = data;
            // console.log(data)
            if (code !== 20000) {
                const warning = new ConfirmDialog({
                    // title: "",
                    warning: true,
                    message
                })
                warning.listen(e => {
                    console.log(e)
                    if (e.behavior === 'close') {
                        if (code === 401000) {
                            document.querySelector('.menus-item-key').click()
                        }
                    }
                })
                return
            }
            return data;
        })
        .catch(error => {
            console.error('Fetch error:', error);
            throw error;
        });
}

export function check_model_exists ( type, name ) {
    return customFetch(`/bizyair/modelhost/check_model_exists`, {
        method: 'POST',
        body: JSON.stringify({ type, name })
    })
}

export function model_upload ( data ) {
    return customFetch('/bizyair/modelhost/model_upload', {
        method: 'POST',
        body: JSON.stringify(data)
    })
}

export function file_upload ( data ) {
    return customFetch('/bizyair/modelhost/file_upload', {
        method: 'POST',
        body: data
    })
}

export function set_api_key ( data ) {
    return customFetch('/bizyair/set_api_key', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: data
    })
}

export function models_files ( data ) {
    return customFetch(`/bizyair/modelhost/models/files?type=${data}`, {method: 'GET'})
}

export function model_types () {
    return customFetch('/bizyair/modelhost/model_types', {method: 'GET'})
}

export function delModels ( data ) {
    return customFetch(`/bizyair/modelhost/models`, {
        method: 'DELETE',
        body: JSON.stringify({
            type: data.type,
            name: data.name,
        }),
    })
}
