import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
    const category = params.category;

    let items = [];
    let allTags: string[] = [];
    let error = '';

    try {
        const [itemsRes, tagsRes] = await Promise.all([
            fetch(`http://localhost:8000/api/items/${category}`),
            fetch('http://localhost:8000/api/tags').catch(() => null)
        ]);

        if (!itemsRes.ok) {
            error = `Не удалось загрузить данные для категории «${category}»: ${itemsRes.status}`;
        } else {
            items = await itemsRes.json();
        }

        if (tagsRes && tagsRes.ok) {
            allTags = await tagsRes.json();
        }
    } catch (err) {
        error = `Ошибка подключения к серверу. Убедитесь, что бэкенд запущен.`;
    }

    return { category, items, allTags, error };
};
