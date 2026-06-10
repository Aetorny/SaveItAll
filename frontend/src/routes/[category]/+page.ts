import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
    const category = params.category;
    const response = await fetch(`http://localhost:8000/api/items/${category}`);

    if (!response.ok) {
        return {
            category,
            items: [],
            error: `Не удалось загрузить данные для категории «${category}»: ${response.status}`
        };
    }

    const items = await response.json();
    return { category, items };
};
