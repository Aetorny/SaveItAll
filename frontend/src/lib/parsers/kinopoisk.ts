import type { Importer, ImportedMediaData } from '../types';
import { getMetaContent, normalizeText } from '../utils';

// Публичный токен комьюнити. Работает без регистраций
const PUBLIC_KP_TOKEN = '8c8e1a93-c128-4af4-8461-028d812f22a0';

async function parseKinopoisk(url: string): Promise<ImportedMediaData> {
    const match = url.match(/^https?:\/\/(?:www\.|m\.)?kinopoisk\.ru\/(film|series)\/(\d+)/i);
    if (!match || !match[2]) {
        throw new Error('Не удалось извлечь ID из ссылки Кинопоиска.');
    }

    const kpId = match[2];

    try {
        const apiRes = await fetch(`https://kinopoiskapiunofficial.tech/api/v2.2/films/${kpId}`, {
            headers: { 'X-API-KEY': PUBLIC_KP_TOKEN }
        });
        
        if (apiRes.ok) {
            const data = await apiRes.json();
            return {
                source_url: url,
                title: data.nameRu || data.nameEn || data.nameOriginal || undefined,
                description: data.description || data.shortDescription || undefined,
                cover_url: data.posterUrl || data.posterUrlPreview || undefined,
            };
        }
    } catch {
        // Игнорируем ошибки парсинга конкретного скрипта и пробуем дальше
    }

    let htmlText = '';
    const archiveUrl = `https://web.archive.org/web/2/https://www.kinopoisk.ru/film/${kpId}/`;

    try {
        const proxyRes = await fetch(`http://localhost:8000/api/fetch-url?url=${encodeURIComponent(archiveUrl)}`);
        if (!proxyRes.ok) throw new Error();
        htmlText = await proxyRes.text();
    } catch {
        try {
            const corsProxyUrl = `https://corsproxy.io/?${encodeURIComponent(archiveUrl)}`;
            const res = await fetch(corsProxyUrl);
            if (!res.ok) throw new Error();
            htmlText = await res.text();
        } catch {
            throw new Error('Не удалось получить данные.');
        }
    }

    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, 'text/html');

    let title: string | null | undefined;
    let description: string | null | undefined;
    let cover_url: string | null | undefined;

    const ldScripts = doc.querySelectorAll('script[type="application/ld+json"]');
    for (const script of Array.from(ldScripts)) {
        try {
            const jsonData = JSON.parse(script.textContent || '{}');
            const movieData = Array.isArray(jsonData) 
                ? jsonData.find(item => item['@type'] === 'Movie' || item['@type'] === 'TVSeries') 
                : (jsonData['@type'] === 'Movie' || jsonData['@type'] === 'TVSeries' ? jsonData : null);
            
            if (movieData) {
                title = movieData.name || movieData.alternativeHeadline;
                description = movieData.description;
                cover_url = movieData.image;
                break;
            }
        } catch {
            continue;
        }
    }

    title = title
        || getMetaContent(doc, 'meta[property="og:title"]')
        || getMetaContent(doc, 'meta[name="twitter:title"]')
        || normalizeText(doc.querySelector('h1[itemprop="name"]')?.textContent)
        || normalizeText(doc.title);

    description = description
        || getMetaContent(doc, 'meta[property="og:description"]')
        || getMetaContent(doc, 'meta[name="description"]');

    cover_url = cover_url
        || getMetaContent(doc, 'meta[property="og:image"]');

    if (title) {
        title = title.replace(/\s*[—\-]\s*Кинопоиск.*$/i, '').trim();
        title = title.replace(/\s*[—\-]\s*смотреть онлайн.*$/i, '').trim();
        title = title.replace(/\s*\(Фильм.*?\)/i, '').trim();
    }

    if (cover_url && cover_url.startsWith('//')) {
        cover_url = 'https:' + cover_url;
    }

    if (!title && !description) {
        throw new Error('Не удалось спарсить данные с Кинопоиска.');
    }

    return {
        source_url: url,
        title: title || undefined,
        description: description || undefined,
        cover_url: cover_url || undefined,
    };
}

export const kinopoiskImporter: Importer = {
    id: 'kinopoisk',
    name: 'Кинопоиск',
    urlPattern: /^https?:\/\/(?:www\.|m\.)?kinopoisk\.ru\/(film|series)\/\d+/i,
    fetchAndParse: parseKinopoisk,
};