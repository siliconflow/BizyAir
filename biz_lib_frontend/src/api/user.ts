import { customFetch } from '@/utils/customFetch';

export const set_api_key = (data: any) => customFetch('/bizyair/set_api_key', {
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
