import type { Importer, ImportedMediaData } from '../types';
import { normalizeText } from '../utils';

async function parseRemanga(url: string): Promise<ImportedMediaData> {
    let match = url.match(/^https?:\/\/(?:www\.)?remanga\.org\/manga\/([^\/?#]+)/i);
    if (!match || !match[1]) {
        match = url.match(/^https?:\/\/(?:www\.)?xn--80aaig9ahr\.xn--c1avg\/manga\/([^\/?#]+)/i);
        if (!match || !match[1]) {
            match = url.match(/^https?:\/\/(?:www\.)?реманга\.орг\/manga\/([^\/?#]+)/i);
            if (!match || !match[1]) {
                throw new Error('Не удалось извлечь название манги из ссылки Remanga.');
            }
        }
    }

    const slug = match[1];
    const apiUrl = `https://api.remanga.org/api/titles/${slug}/`;

    let jsonText = '';

    try {
        const proxyRes = await fetch(`http://localhost:8000/api/fetch-url?url=${encodeURIComponent(apiUrl)}`);
        if (!proxyRes.ok) throw new Error();
        jsonText = await proxyRes.text();
    } catch {
        try {
            const corsProxyUrl = `https://corsproxy.io/?${encodeURIComponent(apiUrl)}`;
            const res = await fetch(corsProxyUrl);
            if (!res.ok) throw new Error();
            jsonText = await res.text();
        } catch {
            throw new Error('Не удалось получить данные с API Remanga.');
        }
    }

    let data;
    try {
        data = JSON.parse(jsonText);
    } catch (e) {
        throw new Error('Remanga API вернул неверный формат данных (ожидался JSON).');
    }

    if (!data || !data.content) {
        throw new Error('Манга не найдена или API Remanga вернул ошибку.');
    }

    const content = data.content;

    let title: string | null | undefined = content.rus_name || content.en_name || content.main_name;
    let description: string | null | undefined = content.description;
    let cover_url: string | null | undefined = content.img?.high || content.img?.mid || content.img?.low;

    if (description) {
        description = description.replace(/<[^>]*>?/gm, '').trim();
        description = normalizeText(description); 
    }

    if (title) {
        title = normalizeText(title);
    }

    if (cover_url) {
        if (cover_url.startsWith('//')) {
            cover_url = 'https:' + cover_url;
        } else if (cover_url.startsWith('/')) {
            cover_url = 'https://remanga.org' + cover_url;
        }
    }

    return {
        source_url: `https://remanga.org/manga/${slug}`,
        title: title || undefined,
        description: description || undefined,
        cover_url: cover_url || undefined,
    };
}

export const remangaImporter: Importer = {
    id: 'remanga',
    name: 'Remanga',
    urlPattern: /^https?:\/\/(?:www\.)?remanga\.org\/manga\/[^\/]+/i,
    fetchAndParse: parseRemanga,
};

export const remangaAlternativeImporter: Importer = {
    id: 'remanga-alt',
    name: 'Реманга',
    urlPattern: /^https?:\/\/(?:www\.)?xn--80aaig9ahr\.xn--c1avg\/manga\/[^\/]+/i,
    fetchAndParse: parseRemanga,
};

export const remangaAlternativeRussianImporter: Importer = {
    id: 'remanga-alt-ru',
    name: 'Реманга',
    urlPattern: /^https?:\/\/(?:www\.)?реманга\.орг\/manga\/[^\/]+/i,
    fetchAndParse: parseRemanga,
};
