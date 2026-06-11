import type { Importer } from './types';
import { shikimoriImporter } from './parsers/shikimori';
import { steamImporter } from './parsers/steam';

// Реэкспорт типов, чтобы они были доступны снаружи через `import { ImportedMediaData } from './importers'`
export * from './types';

// Реестр всех импортеров
export const importers: Importer[] = [
    shikimoriImporter,
    steamImporter,
    // При добавлении нового парсера просто импортируем и добавляем его сюда
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