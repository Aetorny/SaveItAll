export type ImportedMediaData = {
    title?: string;
    description?: string;
    cover_url?: string;
    source_url: string;
};

export type Importer = {
    id: string;
    name: string;
    urlPattern: RegExp;
    parseHtml: (html: string, url: string) => ImportedMediaData;
};

function getMetaContent(doc: Document, selector: string): string | null {
    const el = doc.querySelector(selector) as HTMLMetaElement | null;
    return el?.content?.trim() || null;
}

function normalizeText(value: string | null | undefined): string | undefined {
    if (!value) return undefined;
    const text = value.trim();
    return text.length ? text : undefined;
}

function getDescriptionTextFromNode(node: Element | null): string | undefined {
    if (!node) return undefined;
    const rawText = node.textContent?.trim();
    return normalizeText(rawText);
}

function getDescriptionHtmlFromNode(node: Element | null): string | undefined {
    if (!node) return undefined;
    const html = node.innerHTML?.trim();
    return normalizeText(html);
}

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

export const importers: Importer[] = [
    {
        id: 'shikimori',
        name: 'Shikimori',
        urlPattern: /^https?:\/\/shikimori\.io\/animes\/\d+[\w-]*/i,
        parseHtml: parseShikimori,
    },
];

export function findImporter(url: string | undefined): Importer | null {
    if (!url) return null;
    try {
        const normalizedUrl = url.trim();
        if (!normalizedUrl) return null;
        return importers.find((importer) => importer.urlPattern.test(normalizedUrl)) ?? null;
    } catch {
        return null;
    }
}
