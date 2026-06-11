import type { Importer, ImportedMediaData } from '../types';
import {
    getMetaContent,
    normalizeText,
    getDescriptionHtmlFromNode
} from '../utils';

function parseLitres(html: string, url: string): ImportedMediaData {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    const title = normalizeText(doc.querySelector('h1[itemprop="name"]')?.textContent)
        || normalizeText(doc.querySelector('h1')?.textContent)
        || getMetaContent(doc, 'meta[property="og:title"]')
        || normalizeText(doc.title);

    let description: string | null | undefined;

    try {
        const nextScript = doc.querySelector('#__NEXT_DATA__');
        if (nextScript && nextScript.textContent) {
            const htmlAnnMatch = nextScript.textContent.match(/"html_annotation":"((?:[^"\\]|\\.)*)"/);
            if (htmlAnnMatch && htmlAnnMatch[1]) {
                description = JSON.parse(`"${htmlAnnMatch[1]}"`);
            } else {
                const annMatch = nextScript.textContent.match(/"annotation":"((?:[^"\\]|\\.)*)"/);
                if (annMatch && annMatch[1]) {
                    description = JSON.parse(`"${annMatch[1]}"`);
                }
            }
        }
    } catch (e) {
        // Если парсинг JSON провалился, просто игнорируем и продолжим с другими методами
    }

    if (!description || description.endsWith('…') || description.endsWith('...')) {
        const ldScripts = doc.querySelectorAll('script[type="application/ld+json"]');
        for (const script of Array.from(ldScripts)) {
            try {
                const data = JSON.parse(script.textContent || '');
                if ((data['@type'] === 'Book' || data['@type'] === 'Audiobook') && data.description) {
                    if (!data.description.endsWith('…')) {
                        description = data.description;
                        break;
                    }
                }
            } catch (e) {}
        }
    }

    if (!description || description.endsWith('…') || description.endsWith('...')) {
        const nodes = [
            doc.querySelector('div[class*="BookCard-module__annotation"]'),
            doc.querySelector('div[class*="Annotation-module__text"]'),
            doc.querySelector('[itemprop="about"]'),
            doc.querySelector('[itemprop="description"]')
        ];
        
        for (const node of nodes) {
            if (!node) continue;
            const html = getDescriptionHtmlFromNode(node);
            if (html) {
                if (!description) description = html;
                if (!html.includes('…') && !html.includes('...')) {
                    description = html;
                    break;
                }
            }
        }
    }

    if (!description) {
        description = getMetaContent(doc, 'meta[property="og:description"]')
            || getMetaContent(doc, 'meta[name="description"]');
    }

    const cover_url = getMetaContent(doc, 'meta[property="og:image"]')
        || doc.querySelector('img[itemprop="image"]')?.getAttribute('src')
        || doc.querySelector('picture img[class*="Cover"]')?.getAttribute('src')
        || undefined;

    let normalizedCover: string | undefined = undefined;
    if (cover_url) {
        const cuRaw = cover_url.trim();
        try {
            normalizedCover = new URL(cuRaw, url).href;
        } catch (e) {
            if (cuRaw.startsWith('//')) normalizedCover = 'https:' + cuRaw;
            else if (cuRaw.startsWith('/')) normalizedCover = 'https://www.litres.ru' + cuRaw;
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

export const litresImporter: Importer = {
    id: 'litres',
    name: 'ЛитРес',
    urlPattern: /^https?:\/\/(www\.)?litres\.ru\/(book|audiobook)\/[^\/]+/i,
    parseHtml: parseLitres,
};
