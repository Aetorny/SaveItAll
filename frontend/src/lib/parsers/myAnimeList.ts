import type { Importer, ImportedMediaData } from '../types';
import {
    getMetaContent,
    normalizeText,
    getDescriptionHtmlFromNode,
    getDescriptionTextFromNode
} from '../utils';

function parseMyAnimeList(html: string, url: string): ImportedMediaData {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // 1. Извлечение названия (у MAL обычно h1.title-name, либо берем из мета-тегов)
    const title = normalizeText(doc.querySelector('h1.title-name')?.textContent)
        || normalizeText(doc.querySelector('.title-name strong')?.textContent)
        || getMetaContent(doc, 'meta[property="og:title"]')
        || getMetaContent(doc, 'meta[name="twitter:title"]')
        || normalizeText(doc.title);

    // 2. Извлечение синопсиса (у MAL он лежит в span с itemprop="description")
    const descriptionNode = doc.querySelector('span[itemprop="description"]');
    const description = descriptionNode ? normalizeText(descriptionNode.textContent) : getDescriptionHtmlFromNode(doc.querySelector('[itemprop="description"]'))
        || getMetaContent(doc, 'meta[property="og:description"]')
        || getMetaContent(doc, 'meta[name="description"]')
        || getDescriptionTextFromNode(doc.querySelector('.manga-introduction')) // на случай старых/специфичных страниц манги
        || getDescriptionTextFromNode(doc.querySelector('.profile-about-string'));

    // 3. Извлечение обложки (основное изображение имеет атрибут itemprop="image")
    const cover_url = doc.querySelector('img[itemprop="image"]')?.getAttribute('src')
        || doc.querySelector('.leftside img')?.getAttribute('src')
        || doc.querySelector('a[href*="/pics"] img')?.getAttribute('src')
        || getMetaContent(doc, 'meta[property="og:image"]')
        || undefined;

    // 4. Нормализация ссылки на обложку
    let normalizedCover: string | undefined = undefined;
    if (cover_url) {
        const cuRaw = cover_url.trim();
        try {
            normalizedCover = new URL(cuRaw, url).href;
        } catch (e) {
            if (cuRaw.startsWith('//')) normalizedCover = 'https:' + cuRaw;
            else if (cuRaw.startsWith('/')) normalizedCover = 'https://myanimelist.net' + cuRaw;
            else normalizedCover = cuRaw;
        }
    }

    return {
        source_url: url,
        title: title ?? undefined,
        description: description ?? undefined,
        cover_url: normalizedCover,
    };
}

export const myanimelistImporter: Importer = {
    id: 'myanimelist',
    name: 'MyAnimeList',
    urlPattern: /^https?:\/\/myanimelist\.net\/(anime|manga)\/\d+/i,
    parseHtml: parseMyAnimeList,
};