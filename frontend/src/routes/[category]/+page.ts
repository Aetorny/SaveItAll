import type { PageLoad } from './$types';
import { api } from '$lib/api';

export const load: PageLoad = async ({ params }) => {
    const category = params.category;
    let items = [];
    let allTags: string[] = [];
    let error = '';

    try {
        const [itemsRes, tagsRes] = await Promise.allSettled([
            api.getItems(category),
            api.getTags()
        ]);

        if (itemsRes.status === 'fulfilled') {
            items = itemsRes.value;
        } else {
            error = `Не удалось загрузить данные для категории «${category}»`;
        }

        if (tagsRes.status === 'fulfilled') {
            allTags = tagsRes.value;
        }
    } catch (err) {
        error = `Ошибка подключения к серверу. Убедитесь, что бэкенд запущен.`;
    }

    return { category, items, allTags, error };
};