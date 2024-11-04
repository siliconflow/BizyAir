import { customFetch } from '@/utils/customFetch';

let host = `${window.location.origin}${window.location.pathname === '/' ? '' : window.location.pathname}`
export const set_api_key = (data: any) => fetch(`${host}/bizyair/set_api_key`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: data
})

export const getUserInfo = () => customFetch('/bizyair/user/info?v=1', { method: 'get' })

export const putShareId = (data: any) => customFetch('/bizyair/user/share_id', {
    method: 'put',
    body: JSON.stringify(data)
})
