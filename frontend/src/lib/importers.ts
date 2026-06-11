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
    parseHtml?: (html: string, url: string) => ImportedMediaData;
    fetchAndParse?: (url: string) => Promise<ImportedMediaData>;
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

async function parseSteam(url: string): Promise<ImportedMediaData> {
    const match = url.match(/^https?:\/\/store\.steampowered\.com\/app\/(\d+)/i);
    if (!match || !match[1]) {
        throw new Error('Не удалось извлечь Steam AppID из ссылки.');
    }
    
    const appId = match[1];
    const apiUrl = `https://store.steampowered.com/api/appdetails?appids=${appId}&l=russian`;

    let jsonText: string;
    try {
        const proxyRes = await fetch(`http://localhost:8000/api/fetch-url?url=${encodeURIComponent(apiUrl)}`);
        if (!proxyRes.ok) throw new Error('Backend proxy failed');
        jsonText = await proxyRes.text();
    } catch {
        try {
            const corsProxyUrl = `https://corsproxy.io/?${encodeURIComponent(apiUrl)}`;
            const res = await fetch(corsProxyUrl);
            if (!res.ok) throw new Error('CORS proxy failed');
            jsonText = await res.text();
        } catch (e) {
            throw new Error('Не удалось получить данные из Steam. Проверьте CORS или бэкенд-прокси.');
        }
    }

    const data = JSON.parse(jsonText);
    const appData = data[appId];

    if (!appData || !appData.success) {
        throw new Error('Игра не найдена в Steam или данные недоступны.');
    }

    const game = appData.data;

    return {
        source_url: url,
        title: game.name,
        description: game.short_description || game.about_the_game || '',
        cover_url: `https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/${appId}/library_600x900.jpg` || undefined,
    };
}

export const importers: Importer[] = [
    {
        id: 'shikimori',
        name: 'Shikimori',
        urlPattern: /^https?:\/\/shikimori\.io\/animes\/[^\/]+/i,
        parseHtml: parseShikimori,
    },
    {
        id: 'steam',
        name: 'Steam',
        urlPattern: /^https?:\/\/store\.steampowered\.com\/app\/\d+/i,
        fetchAndParse: parseSteam,
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