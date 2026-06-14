const BASE_URL = 'http://localhost:8000/api';

export const api = {
    async getItems(category: string) {
        const res = await fetch(`${BASE_URL}/items/${category}`);
        if (!res.ok) throw new Error(`Ошибка: ${res.status}`);
        return res.json();
    },
    
    async getTags() {
        const res = await fetch(`${BASE_URL}/tags`);
        if (!res.ok) throw new Error(`Ошибка: ${res.status}`);
        return res.json();
    },

    async createTag(tag: string) {
        return fetch(`${BASE_URL}/create-tag?tag=${encodeURIComponent(tag)}`, { method: 'POST' });
    },

    async deleteTag(tag: string) {
        return fetch(`${BASE_URL}/delete-tag?tag=${encodeURIComponent(tag)}`, { method: 'POST' });
    },

    async addTagToItem(itemId: number, tag: string) {
        const res = await fetch(`${BASE_URL}/add-tag/${itemId}?tag=${encodeURIComponent(tag)}`);
        if (!res.ok) throw new Error('Failed to add tag');
        return res.json();
    },

    async removeTagFromItem(itemId: number, tag: string) {
        const res = await fetch(`${BASE_URL}/remove-tag/${itemId}?tag=${encodeURIComponent(tag)}`);
        if (!res.ok) throw new Error('Failed to remove tag');
        return res.json();
    },

    async saveItem(payload: any, id?: number | null) {
        const url = id ? `${BASE_URL}/items/${id}` : `${BASE_URL}/items/`;
        const method = id ? 'PUT' : 'POST';
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Произошла ошибка');
        }
        return res.json();
    },

    async deleteItem(id: number) {
        return fetch(`${BASE_URL}/items/${id}`, { method: 'DELETE' });
    },

    async fetchProxy(url: string) {
        const proxyUrl = `${BASE_URL}/fetch-url?url=${encodeURIComponent(url)}`;
        const res = await fetch(proxyUrl);
        if (!res.ok) throw new Error(`Не удалось загрузить страницу: ${await res.text()}`);
        return res.text();
    }
};