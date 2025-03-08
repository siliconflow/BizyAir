import { dialog } from './subassembly/dialog.js';

const fetchCache = new Map();

function customFetch(url, options = {}) {
    const now = Date.now();
    if (fetchCache.has(url)) {
        const lastFetchTime = fetchCache.get(url);
        if (now - lastFetchTime < 1200) {
            return Promise.resolve(null);
        }
    }
    fetchCache.set(url, now);
    const host = `${window.location.origin}${window.location.pathname === '/' ? '' : window.location.pathname}`
    return window.fetch(`${host}${url}`, options)
        .then(response => {
            if (response.status === 404) {
                dialog({
                    content: "You may be missing dependencies at the moment. For details, please refer to the ComfyUI logs.",
                    type: 'error',
                    noText: 'Close'
                })
            }
            return response.json();
        })
        .then(data => {
            const { code, message } = data;
            if (code !== 20000) {
                dialog({
                    type: 'warning',
                    content: message,
                    noText: 'Close',
                    onNo: () => {
                        if (code === 401000) {
                            document.querySelector('.menus-item-key').click()
                        }
                    }
                })

                return;
            }
            return data;
        })
        .catch(error => {
            console.error('Fetch error:', error);
            throw error;
        });
}


export function check_model_exists ( type, name ) {
    return customFetch('/bizyair/modelhost/check_model_exists', {
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

export function models_files ( params, data ) {
    let actualParams = ''
    for (const i in params) {
        actualParams += `${i}=${params[i]}&`
    }
    return customFetch(`/bizyair/community/models/query?${actualParams}`, {
        method: 'POST',
        body: JSON.stringify(data)
    })
}

export function change_public ( data ) {
    return customFetch('/bizyair/modelhost/models/change_public', {method: 'PUT', body: JSON.stringify(data)})
}

export function model_types () {
    return customFetch('/bizyair/community/model_types', {method: 'GET'})
}

export function check_folder (url) {
    return customFetch(`/bizyair/modelhost/check_folder?absolute_path=${encodeURIComponent(url)}`, {method: 'GET'})
}

export function submit_upload (data) {
    return customFetch(`/bizyair/community/submit_upload?clientId=${sessionStorage.getItem('clientId')}`, {
        method: 'POST',
        body: JSON.stringify(data)
    })
}

export function delModels ( data ) {
    return customFetch('/bizyair/modelhost/models', {
        method: 'DELETE',
        body: JSON.stringify({
            type: data.type,
            name: data.name,
        }),
    })
}

export function getUserInfo () {
    return customFetch('/bizyair/user/info', { method: 'get' })
}

export function putShareId (data) {
    return customFetch('/bizyair/user/share_id', {
        method: 'put',
        body: JSON.stringify(data)
    })
}

export function getDescription (data) {
    return customFetch(`/bizyair/modelhost/models/description?${new URLSearchParams(data).toString()}`, {
        method: 'get'
    })
}

export function putDescription (data) {
    return customFetch('/bizyair/modelhost/models/description', {
        method: 'put',
        body: JSON.stringify(data)
    })
}

export function uploadImage (file) {
    const formData = new FormData();
    formData.append('file', file);
    return customFetch('/bizyair/community/files/upload', {
        method: 'POST',
        body: formData
    })
}
