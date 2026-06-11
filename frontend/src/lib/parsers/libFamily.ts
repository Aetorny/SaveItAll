import type { Importer, ImportedMediaData } from '../types';

interface LibSiteConfig {
    id: string;
    name: string;
    baseUrl: string;
    siteId: number;
    pathSegment: string;
}

const LIB_SITES: LibSiteConfig[] = [
    {
        id: 'mangalib',
        name: 'MangaLib',
        baseUrl: 'https://mangalib.org',
        siteId: 1,
        pathSegment: 'manga',
    },
    {
        id: 'mangalib',
        name: 'MangaLib',
        baseUrl: 'https://mangalib.me',
        siteId: 1,
        pathSegment: 'manga',
    },
    {
        id: 'ranobelib',
        name: 'RanobeLib',
        baseUrl: 'https://ranobelib.me',
        siteId: 3,
        pathSegment: 'book',
    },
    {
        id: 'hentailib',
        name: 'HentaiLib',
        baseUrl: 'https://hentailib.me',
        siteId: 4,
        pathSegment: 'manga',
    }
];

const API_DOMAIN = 'https://api.cdnlibs.org';

interface SummaryNode {
    type: string;
    text?: string;
    content?: SummaryNode[];
    marks?: Array<{ type: string; attrs?: Record<string, unknown> }>;
}

interface LibApiResponse {
    data: {
        id: number;
        name: string;
        rus_name: string;
        eng_name?: string;
        slug: string;
        slug_url: string;
        cover?: {
            thumbnail: string;
            default: string;
            md: string;
        };
        summary?: SummaryNode;
    };
}

function escapeHtml(text: string): string {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function summaryToHtml(summary: SummaryNode | null | undefined): string {
    if (!summary) return '';

    if (summary.type === 'text') {
        let text = escapeHtml(summary.text ?? '');
        if (summary.marks) {
            for (const mark of summary.marks) {
                if (mark.type === 'bold') text = `<strong>${text}</strong>`;
                if (mark.type === 'italic') text = `<em>${text}</em>`;
                if (mark.type === 'link' && mark.attrs?.['href']) {
                    text = `<a href="${escapeHtml(String(mark.attrs['href']))}">${text}</a>`;
                }
            }
        }
        return text;
    }

    if (!summary.content || summary.content.length === 0) {
        if (summary.type === 'hardBreak') return '<br>';
        return '';
    }

    const inner = summary.content.map(child => summaryToHtml(child)).join('');

    switch (summary.type) {
        case 'paragraph':
            return `<p>${inner}</p>`;
        case 'blockquote':
            return `<blockquote>${inner}</blockquote>`;
        case 'heading':
            return `<h3>${inner}</h3>`;
        case 'bulletList':
            return `<ul>${inner}</ul>`;
        case 'orderedList':
            return `<ol>${inner}</ol>`;
        case 'listItem':
            return `<li>${inner}</li>`;
        case 'doc':
        default:
            return inner;
    }
}

function extractSlugUrl(url: string): string | null {
    const match = url.match(/\/ru\/(?:manga|book)\/([^/?#]+)/i);
    return match?.[1] ?? null;
}

function detectSite(url: string): LibSiteConfig | null {
    for (const site of LIB_SITES) {
        const host = site.baseUrl.replace('https://', '');
        if (url.includes(host)) {
            return site;
        }
    }
    return null;
}

async function parseLibGroup(url: string): Promise<ImportedMediaData> {
    const siteConfig = detectSite(url);
    if (!siteConfig) {
        throw new Error('Неподдерживаемый сайт. Поддерживаются: mangalib.org, ranobelib.me');
    }

    const slugUrl = extractSlugUrl(url);
    if (!slugUrl) {
        throw new Error('Не удалось извлечь slug из ссылки.');
    }

    const apiUrl = `${API_DOMAIN}/api/manga/${slugUrl}?fields[]=summary&fields[]=eng_name&fields[]=otherNames`;

    let jsonText: string;
    try {
        const proxyRes = await fetch(`http://localhost:8000/api/fetch-url?url=${encodeURIComponent(apiUrl)}&referer=${encodeURIComponent(siteConfig.baseUrl)}`);
        if (!proxyRes.ok) throw new Error('Backend proxy failed');
        jsonText = await proxyRes.text();
    } catch {
        try {
            const res = await fetch(apiUrl, {
                headers: {
                    'Accept': 'application/json',
                    'Referer': siteConfig.baseUrl,
                    'Site-Id': siteConfig.siteId.toString(),
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                },
            });
            if (!res.ok) throw new Error(`API returned ${res.status}`);
            jsonText = await res.text();
        } catch (e) {
            throw new Error(`Не удалось получить данные из ${siteConfig.name}. Проверьте CORS или бэкенд-прокси.`);
        }
    }

    const response: LibApiResponse = JSON.parse(jsonText);
    const data = response.data;

    if (!data || !data.id) {
        throw new Error(`Тайтл не найден на ${siteConfig.name}.`);
    }

    return {
        source_url: url,
        title: data.rus_name || data.eng_name || data.name || undefined,
        description: data.summary ? summaryToHtml(data.summary) || undefined : undefined,
        cover_url: data.cover?.default || data.cover?.md || data.cover?.thumbnail || undefined,
    };
}

export const libFamilyImporter: Importer = {
    id: '...lib',
    name: 'MangaLib / RanobeLib / HentaiLib',
    urlPattern: /^https?:\/\/(mangalib\.org|mangalib\.me|hentailib\.me|ranobelib\.me)\/ru\/(manga|book)\/[^/?#]+/i,
    fetchAndParse: parseLibGroup,
};
