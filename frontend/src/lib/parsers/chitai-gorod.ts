import type { Importer, ImportedMediaData } from '../types';
import {
    getMetaContent,
    normalizeText,
    getDescriptionHtmlFromNode
} from '../utils';

function parseChitaiGorod(html: string, url: string): ImportedMediaData {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    const title = normalizeText(doc.querySelector('h1[itemprop="name"]')?.textContent)
        || normalizeText(doc.querySelector('h1.detail-title__text')?.textContent)
        || normalizeText(doc.querySelector('h1')?.textContent)
        || getMetaContent(doc, 'meta[property="og:title"]')
        || normalizeText(doc.title);

    let description: string | undefined;

    const descNodes = [
        doc.querySelector('.detail-description__text'),
        doc.querySelector('.product-detail-features__description'),
        doc.querySelector('div[class*="product-description"]'),
        doc.querySelector('[itemprop="description"]')
    ];

    for (const node of descNodes) {
        if (!node) continue;
        
        const textContent = node.textContent || '';
        if (textContent.includes('В книжном интернет-магазине Читай-город')) {
            continue;
        }

        const htmlContent = getDescriptionHtmlFromNode(node);
        if (htmlContent) {
            description = htmlContent;
            break;
        }
    }

    if (!description) {
        const ldScripts = doc.querySelectorAll('script[type="application/ld+json"]');
        for (const script of Array.from(ldScripts)) {
            try {
                const data = JSON.parse(script.textContent || '');
                const checkObject = (obj: any): string | undefined => {
                    if (!obj || typeof obj !== 'object') return undefined;
                    if (Array.isArray(obj)) {
                        for (const item of obj) {
                            const res = checkObject(item);
                            if (res) return res;
                        }
                    } else {
                        if (obj.description && !obj.description.includes('В книжном интернет-магазине')) {
                            return obj.description;
                        }
                        if (obj['@graph']) {
                            return checkObject(obj['@graph']);
                        }
                    }
                    return undefined;
                };
                
                const foundDesc = checkObject(data);
                if (foundDesc) {
                    description = foundDesc;
                    break;
                }
            } catch (e) {}
        }
    }

    const cover_url = getMetaContent(doc, 'meta[property="og:image"]')
        || doc.querySelector('img[itemprop="image"]')?.getAttribute('src')
        || doc.querySelector('.product-gallery__image')?.getAttribute('src')
        || undefined;

    let normalizedCover: string | undefined = undefined;
    if (cover_url) {
        const cuRaw = cover_url.trim();
        try {
            normalizedCover = new URL(cuRaw, url).href;
        } catch (e) {
            if (cuRaw.startsWith('//')) normalizedCover = 'https:' + cuRaw;
            else if (cuRaw.startsWith('/')) normalizedCover = 'https://www.chitai-gorod.ru' + cuRaw;
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

export const chitaiGorodImporter: Importer = {
    id: 'chitai-gorod',
    name: 'Читай-город',
    urlPattern: /^https?:\/\/(www\.)?chitai-gorod\.ru\/product\/[^\/]+/i,
    parseHtml: parseChitaiGorod,
};
