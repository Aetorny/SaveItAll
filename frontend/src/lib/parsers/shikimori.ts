import type { Importer, ImportedMediaData } from '../types';
import {
    getMetaContent,
    normalizeText,
    getDescriptionHtmlFromNode,
    getDescriptionTextFromNode
} from '../utils';

function parseShikimori(html: string, url: string): ImportedMediaData {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    const title = normalizeText(doc.querySelector('h1')?.textContent)
        || getMetaContent(doc, 'meta[property="og:title"]')
        || getMetaContent(doc, 'meta[name="twitter:title"]')
        || normalizeText(doc.querySelector('h2')?.textContent)
        || normalizeText(doc.title);

    const description = getDescriptionHtmlFromNode(doc.querySelector('.c-description [itemprop="description"]'))
        || getDescriptionHtmlFromNode(doc.querySelector('.c-description .b-text_with_paragraphs'))
        || getDescriptionHtmlFromNode(doc.querySelector('.c-description .text'))
        || getMetaContent(doc, 'meta[property="og:description"]')
        || getMetaContent(doc, 'meta[name="description"]')
        || getDescriptionTextFromNode(doc.querySelector('[itemprop="description"]'))
        || getDescriptionTextFromNode(doc.querySelector('.description'))
        || getDescriptionTextFromNode(doc.querySelector('.anime-description'))
        || getDescriptionTextFromNode(doc.querySelector('.storyline'))
        || getDescriptionTextFromNode(doc.querySelector('.story'));

    const cover_url = doc.querySelector('img[src*="/uploads/poster/animes/"]')?.getAttribute('src')
        || doc.querySelector('img[src*="/uploads/poster/"]')?.getAttribute('src')
        || getMetaContent(doc, 'meta[property="og:image"]')
        || undefined;

    let normalizedCover: string | undefined = undefined;
    if (cover_url) {
        const cuRaw = cover_url.trim();
        try {
            normalizedCover = new URL(cuRaw, url).href;
        } catch (e) {
            if (cuRaw.startsWith('//')) normalizedCover = 'https:' + cuRaw;
            else if (cuRaw.startsWith('/')) normalizedCover = 'https://shikimori.io' + cuRaw;
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

export const shikimoriImporter: Importer = {
    id: 'shikimori',
    name: 'Shikimori',
    urlPattern: /^https?:\/\/shikimori\.io\/animes\/[^\/]+/i,
    parseHtml: parseShikimori,
};