import type { Importer, ImportedMediaData } from '../types';

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

export const steamImporter: Importer = {
    id: 'steam',
    name: 'Steam',
    urlPattern: /^https?:\/\/store\.steampowered\.com\/app\/\d+/i,
    fetchAndParse: parseSteam,
};