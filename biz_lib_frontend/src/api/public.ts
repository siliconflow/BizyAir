import { customFetch } from '@/utils/customFetch';

export const uploadImage = (file: string | Blob) => {
    const formData = new FormData();
    formData.append('file', file);
    return customFetch('/bizyair/community/files/upload', {
        method: 'POST',
        body: formData
    })
}
